import Client from "../utils/Client";
import * as schema from "@fansbot/db/schema";
import { ButtonStyle, ContainerBuilder, MediaGalleryItemBuilder, MessageFlags, time, TimestampStyles } from "discord.js";
import db from "@fansbot/db";
import { getOrFetchGuild, getOrFetchGuildChannel, getOrFetchGuildMessage } from "../utils/getOrFetch";
import { getConfig } from "@fansbot/config";
import * as zodSchema from "@fansbot/db/schema/zod";
import { eq } from "drizzle-orm";

type Channel = typeof schema.channel.$inferSelect;

async function formatSchedule(
    channel: Channel,
    events: any[]
) {
    const bucketConfig = (await getConfig(zodSchema.ConfigKeys.BUCKET)) as zodSchema.Bucket;

    const now = new Date();

    const container = new ContainerBuilder()
        .addMediaGalleryComponents(c =>
            c.addItems(
                new MediaGalleryItemBuilder()
                    .setURL(`${bucketConfig.baseUrl}${channel.banner}`)
            )
        )
        .addTextDisplayComponents(c =>
            c.setContent(`# ${channel.channelName} ${channel.channelRegion ? `[${channel.channelRegion}] Schedule` : ""}`)
        )
        .setAccentColor(Number(`0x${channel.color}`));

    let eventsFmt: string[] = [];

    let liveIndex: number = 0;
    for (const [i, event] of events.entries()) {
        const eventStart = new Date(event.start_time);
        if (eventStart.valueOf() <= now.valueOf() && (i + 1 >= events.length || new Date(events[i + 1].start_time).valueOf() > now.valueOf())) {
            liveIndex = i;
        }
    }

    const startIdx = Math.max(0, liveIndex - 3);
    const endIdx = Math.min(events.length, liveIndex + 1 + 10);

    for (let i = startIdx; i < endIdx; i++) {
        const event = events[i];
        const eventStart = new Date(event.start_time);
        if (i === liveIndex) {
            eventsFmt.push(`:arrow_right: **${time(eventStart, TimestampStyles.ShortTime)} [${event.main_title}](https://bbc.co.uk/programmes/${event.program_id.split("/").at(-1)})**`)
        } else {
            eventsFmt.push(`:black_large_square: ${time(eventStart, TimestampStyles.ShortTime)} [${event.main_title}](https://bbc.co.uk/programmes/${event.program_id.split("/").at(-1)})`)
        }
    }
    container.addTextDisplayComponents(c =>
        c.setContent(eventsFmt.join("\n"))
    );
    container.addSeparatorComponents();
    container.addTextDisplayComponents(c =>
        c.setContent(`-# Last updated: ${time(now, TimestampStyles.LongDateShortTime)}`)
    );
    container.addSectionComponents(c =>
        c.addTextDisplayComponents(tc =>
            tc.setContent("Full schedule:")
        )
            .setButtonAccessory(ac =>
                ac.setURL(`https://bbc.co.uk/schedules/${channel.bbcId}`)
                    .setLabel("Open")
                    .setStyle(ButtonStyle.Link)
            )
    );
    container.addSeparatorComponents();
    container.addTextDisplayComponents(c =>
        c.setContent("-# **This feature is in beta!** Please report any bugs to valbuilded.")
    );

    return container;
}

async function schedulesTask(client: Client<true>) {
    const config = {
        guild: (await getConfig(zodSchema.ConfigKeys.GUILD)) as zodSchema.Guild,
    }

    const now = new Date();
    const midnight = new Date(Date.UTC(
        now.getUTCFullYear(),
        now.getUTCMonth(),
        now.getUTCDate(),
        0, 0, 0, 0
    ));

    const autoChannels = await db.query.autoSchedules.findMany();
    const channels = await db.query.channel.findMany();

    let nids = autoChannels.reduce((prev, cur) => {
        const channel = channels.find((c) => c.sid === cur.sid);

        if (channel && !prev.includes(channel.nid)) {
            prev.push(channel.nid);
        }

        return prev;
    }, [] as string[]);

    type Response = {
        status: "success";
        data: {
            programs: {
                service_id: string;
                title: string;
                events: {
                    program_id: string;
                    event_locator: string;
                    main_title: string;
                    secondary_title: string;
                    image_url: string;
                    start_time: string;
                    duration: string;
                    on_demand?: {
                        start_of_availability: string;
                        end_of_availability: string;
                        player_links: Record<string, Record<string, string>>;
                    };
                    genre: string;
                    fallback_image_url: string;
                    uuid: string;
                }[]
            }[]
        }
    }

    const data: Record<string, Response> = {};

    for (const nid of nids) {
        const req = await fetch(`https://www.freeview.co.uk/api/tv-guide?nid=${nid}&start=${Math.floor(midnight.getTime() / 1000)}`);
        data[nid] = await req.json() as Response;
    }

    autoChannels.forEach(async (ac) => {
        const channel = channels.find((c) => c.sid === ac.sid);

        if (channel) {
            const guild = await getOrFetchGuild(client.guilds, config.guild.id);
            const discordChannel = await getOrFetchGuildChannel(guild.channels, ac.postTo);
            const events = data[channel.nid]?.data.programs.find((p) => p.service_id === ac.sid)?.events!;
            if (discordChannel && discordChannel.isTextBased()) {
                if (ac.messageId && ac.cache) {
                    const msg = await getOrFetchGuildMessage(discordChannel.messages, ac.messageId);

                    if (ac.cache !== events) {
                        const container = await formatSchedule(channel, events);
                        await msg.edit({ components: [container], flags: MessageFlags.IsComponentsV2 });
                        await db.update(schema.autoSchedules).set({ cache: events }).where(eq(schema.autoSchedules.id, ac.id));
                    }
                } else {
                    const container = await formatSchedule(channel, events);
                    const msg = await discordChannel.send({ components: [container], flags: MessageFlags.IsComponentsV2 });
                    await db.update(schema.autoSchedules).set({ cache: events, messageId: msg.id }).where(eq(schema.autoSchedules.id, ac.id));
                }
            }
        }
    })
}

// TODO: Schedule commands

export async function setup(client: Client<true>) {
    await schedulesTask(client);
    const schedulesTaskId = setInterval(() => schedulesTask(client), 15 * 60 * 1000);

    return { tasks: { schedules: schedulesTaskId } };
}