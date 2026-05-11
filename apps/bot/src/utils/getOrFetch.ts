import type { GuildChannelManager, GuildManager, Snowflake, GuildMessageManager } from "discord.js";

export async function getOrFetchGuildChannel(manager: GuildChannelManager, id: Snowflake) {
    return manager.cache.get(id) ?? await manager.fetch(id);
}

export async function getOrFetchGuild(manager: GuildManager, id: Snowflake) {
    return manager.cache.get(id) ?? await manager.fetch(id);
}

export async function getOrFetchGuildMessage(manager: GuildMessageManager, id: Snowflake) {
    return manager.cache.get(id) ?? await manager.fetch(id);
}