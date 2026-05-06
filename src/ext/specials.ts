import { ConfigKeys, getSchemaForKey } from "@/db/schema/zod/config";
import Client from "@/utils/Client";
import { getConfig } from "@/utils/config";
import { getOrFetchGuild, getOrFetchGuildChannel } from "@/utils/getOrFetch";
import { ChannelType } from "discord.js";
import * as z from "zod";

async function specialsTask(client: Client<true>) {
    const guildSchema = getSchemaForKey(ConfigKeys.GUILD);
    const channelsSchema = getSchemaForKey(ConfigKeys.CHANNELS);
    const categoriesSchema = getSchemaForKey(ConfigKeys.CATEGORIES);
    type Guild = z.infer<typeof guildSchema>;
    type Channels = z.infer<typeof channelsSchema>;
    type Categories = z.infer<typeof categoriesSchema>;

    const config = {
        // @ts-ignore
        guild: (await getConfig(ConfigKeys.GUILD)) as Guild,
        channels: await getConfig(ConfigKeys.CHANNELS) as Channels,
        categories: await getConfig(ConfigKeys.CATEGORIES) as Categories
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
    await specialsTask(client);
    const specialsTaskId = setInterval(() => specialsTask(client), 30 * 60 * 1000);

    return { tasks: { specials: specialsTaskId } };
}