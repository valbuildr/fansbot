import Client from "@/utils/Client";
import { Colors, EmbedBuilder, Events, time, TimestampStyles } from "discord.js";
import { getConfig } from "@/utils/config";
import { ConfigKeys, getSchemaForKey } from "@/db/schema/zod/config";
import * as z from "zod";
import { getOrFetchGuild, getOrFetchGuildChannel } from "@/utils/getOrFetch";

function addMemberEvent(client: Client<true>) {
    client.on(Events.GuildMemberAdd, async (member) => {
        const channelsConfigType = getSchemaForKey(ConfigKeys.CHANNELS);
        const guildConfigType = getSchemaForKey(ConfigKeys.GUILD);
        type ChannelsConfig = z.infer<typeof channelsConfigType>;
        type GuildConfig = z.infer<typeof guildConfigType>;

        const config = {
            guild: (await getConfig(ConfigKeys.GUILD)) as GuildConfig,
            channels: (await getConfig(ConfigKeys.CHANNELS)) as ChannelsConfig
        };

        const guild = await getOrFetchGuild(client.guilds, config.guild.id);
        const channel = await getOrFetchGuildChannel(guild.channels, config.channels.newMembers);

        if (channel && channel.isSendable()) {
            const e = new EmbedBuilder()
                .setAuthor({ name: "User Joined", iconURL: member.avatarURL() ?? member.user.avatarURL()! })
                .setDescription(`<@${member.user.id}> (${member.user.username})`)
                .setColor(Colors.Green)
                .addFields(
                    { name: "Joined Discord", value: `${time(member.user.createdAt, TimestampStyles.LongDate)} (${time(member.user.createdAt, TimestampStyles.RelativeTime)})`, inline: false }
                )
                .setTimestamp()
                .setThumbnail(member.avatarURL() ?? member.user.avatarURL()!)
                .setFooter({
                    text: `ID: ${member.user.id}`,
                    iconURL: guild.iconURL()!
                });

            await channel.send({ content: `Welcome to ${guild.name}, <@${member.user.id}>! Please read through our rules in <#${config.channels.rules}> to gain full access to the server.`, embeds: [e] });
        }
    });
}

function removeMemberEvent(client: Client<true>) {
    client.on(Events.GuildMemberRemove, async (member) => {
        const channelsConfigType = getSchemaForKey(ConfigKeys.CHANNELS);
        const guildConfigType = getSchemaForKey(ConfigKeys.GUILD);
        type ChannelsConfig = z.infer<typeof channelsConfigType>;
        type GuildConfig = z.infer<typeof guildConfigType>;

        const config = {
            guild: (await getConfig(ConfigKeys.GUILD)) as GuildConfig,
            channels: (await getConfig(ConfigKeys.CHANNELS)) as ChannelsConfig
        };

        const guild = await getOrFetchGuild(client.guilds, config.guild.id);
        const channel = await getOrFetchGuildChannel(guild.channels, config.channels.newMembers);

        if (channel && channel.isSendable()) {
            const e = new EmbedBuilder()
                .setAuthor({ name: "User Left", iconURL: member.avatarURL() ?? member.user.avatarURL()! })
                .setDescription(`<@${member.user.id}> (${member.user.username})`)
                .setColor(Colors.Red)
                .addFields(
                    { name: "Joined Discord", value: `${time(member.user.createdAt, TimestampStyles.LongDate)} (${time(member.user.createdAt, TimestampStyles.RelativeTime)})`, inline: false },
                    { name: `Joined ${guild.name}`, value: `${time(member.joinedAt!, TimestampStyles.LongDate)} (${time(member.joinedAt!, TimestampStyles.RelativeTime)})`, inline: false }
                )
                .setTimestamp()
                .setThumbnail(member.avatarURL() ?? member.user.avatarURL()!)
                .setFooter({
                    text: `ID: ${member.user.id}`,
                    iconURL: guild.iconURL()!
                });

            await channel.send({ embeds: [e] });
        }
    });
}

export async function setup(client: Client<true>) {
    addMemberEvent(client);
    removeMemberEvent(client);
}