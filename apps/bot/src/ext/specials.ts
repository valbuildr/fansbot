import * as zodSchema from "@fansbot/db/schema/zod";
import Client from "../utils/Client";
import { getConfig } from "@fansbot/config";
import { getOrFetchGuild, getOrFetchGuildChannel } from "../utils/getOrFetch";
import { ChannelType } from "discord.js";

async function specialsChannelMoving(client: Client<true>) {
    const config = {
        guild: await getConfig(zodSchema.ConfigKeys.GUILD) as zodSchema.Guild,
        channels: await getConfig(zodSchema.ConfigKeys.CHANNELS) as zodSchema.Channels,
        categories: await getConfig(zodSchema.ConfigKeys.CATEGORIES) as zodSchema.Categories
    };

    const guild = await getOrFetchGuild(client.guilds, config.guild.id);
    const channel = await getOrFetchGuildChannel(guild.channels, config.channels.specials);

    if (channel && channel.type === ChannelType.GuildForum) {
        const activePosts = channel.threads.cache.filter((t) => (
            !t.appliedTags.includes("Archived") &&
            !t.archived &&
            !t.locked
        )).map((v) => v);

        if (activePosts.length === 0) {
            await channel.edit({ parent: config.categories.other });
        } else {
            await channel.edit({ parent: config.categories.main });
        }
    }
}

// export const slashCommands: SlashCommandData[] = [];

export async function setup(client: Client<true>) {
    await specialsChannelMoving(client);
    const specialsChannelMovingId = setInterval(() => specialsChannelMoving(client), 30 * 60 * 1000);

    return { tasks: { specials: specialsChannelMovingId } };
}