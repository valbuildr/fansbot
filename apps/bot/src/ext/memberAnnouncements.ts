import Client from "../utils/Client";
import { Colors, EmbedBuilder, Events, time, TimestampStyles } from "discord.js";
import { getConfig } from "@fansbot/config";
import * as zodSchema from "@fansbot/db/schema/zod";
import { getOrFetchGuild, getOrFetchGuildChannel } from "../utils/getOrFetch";

function addMemberEvent(client: Client<true>) {
    client.on(Events.GuildMemberAdd, async (member) => {
        const config = {
            guild: (await getConfig(zodSchema.ConfigKeys.GUILD)) as zodSchema.Guild,
            channels: (await getConfig(zodSchema.ConfigKeys.CHANNELS)) as zodSchema.Channels
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
        const config = {
            guild: (await getConfig(zodSchema.ConfigKeys.GUILD)) as zodSchema.Guild,
            channels: (await getConfig(zodSchema.ConfigKeys.CHANNELS)) as zodSchema.Channels
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