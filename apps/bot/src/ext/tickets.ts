import type { SlashCommandData } from "../ext";
import { ButtonInteraction, ChannelType, Colors, EmbedBuilder, GuildMember, InteractionContextType, MessageFlags, PermissionsBitField, Role, SlashCommandBuilder, type GuildTextBasedChannel, Events, ActionRowBuilder, ButtonBuilder, ButtonStyle, CategoryChannel } from "discord.js";
import * as zodConfig from "@fansbot/db/schema/zod";
import { getConfig } from "@fansbot/config";
import snowflake from "@fansbot/snowflake";
import { getOrFetchGuild, getOrFetchGuildChannel } from "../utils/getOrFetch";
import type Client from "../utils/Client";

async function ticketClearing(client: Client<true>) {
    const config = {
        guild: (await getConfig(zodConfig.ConfigKeys.GUILD)) as zodConfig.Guild,
        categories: (await getConfig(zodConfig.ConfigKeys.CATEGORIES)) as zodConfig.Categories,
    };

    const guild = await getOrFetchGuild(client.guilds, config.guild.id);
    const category = await getOrFetchGuildChannel(guild.channels, config.categories.tickets) as CategoryChannel;

    for (const channel of category.children.cache.map((c) => c).filter((c) => c.name.startsWith("closed-"))) {
        if (channel.type === ChannelType.GuildText) {
            const diff = Date.now() - new Date(channel.topic ?? "").getTime();
            if (diff >= 3 * 24 * 60 * 60 * 1000) {
                await channel.delete();
            }
        }
    }
}

async function ticketInteractionCheck(client: Client<true>) {
    const config = {
        guild: (await getConfig(zodConfig.ConfigKeys.GUILD)) as zodConfig.Guild,
        categories: (await getConfig(zodConfig.ConfigKeys.CATEGORIES)) as zodConfig.Categories,
    };

    const guild = await getOrFetchGuild(client.guilds, config.guild.id);
    const category = await getOrFetchGuildChannel(guild.channels, config.categories.tickets) as CategoryChannel;

    for (const channel of category.children.cache.map((c) => c).filter((c) => c.name.startsWith("ticket-"))) {
        if (channel.type === ChannelType.GuildText) {
            (await channel.messages.fetch({ limit: 1 })).forEach(async (m) => {
                const diff = Date.now() - m.createdAt.getTime();
                if (diff >= 24 * 60 * 60 * 1000) {
                    const row = new ActionRowBuilder<ButtonBuilder>()
                        .addComponents(
                            new ButtonBuilder()
                                .setCustomId(`ticket-close-${channel.id}`)
                                .setStyle(ButtonStyle.Secondary)
                                .setEmoji("🔒")
                                .setLabel("Close ticket")
                        );

                    await channel.send({ content: "**There hasn't been a message in this ticket for over 24 hours.**\nIf this ticket is no longer needed, please close it.", components: [row] });
                }
            })
        }
    }
}

async function ticketButtonHandler(interaction: ButtonInteraction) {
    const config = {
        categories: (await getConfig(zodConfig.ConfigKeys.CATEGORIES)) as zodConfig.Categories,
        roles: (await getConfig(zodConfig.ConfigKeys.ROLES)) as zodConfig.Roles,
    };

    if (interaction.customId.startsWith("ticket-close-")) {
        if (interaction.guild) {
            if (
                interaction.message.channel.type == ChannelType.GuildText &&
                interaction.message.channel.parentId === config.categories.tickets &&
                interaction.message.channel.name.startsWith("ticket-")
            ) {
                const auth = interaction.message.channel.permissionsFor(interaction.user.id)?.has([PermissionsBitField.Flags.ViewChannel, PermissionsBitField.Flags.SendMessages]);

                if (auth) {
                    const newOverwrites = interaction.message.channel.permissionOverwrites.cache.map((p) => {
                        if (p.id !== interaction.client.user.id && p.id !== config.roles.helper && p.id !== config.roles.mod && p.id !== interaction.guild!.roles.everyone.id) {
                            return {
                                id: p.id,
                                deny: [PermissionsBitField.Flags.SendMessages],
                                allow: [PermissionsBitField.Flags.ViewChannel]
                            };
                        } else {
                            return p;
                        }
                    });
                    await interaction.message.channel.permissionOverwrites.set(newOverwrites);

                    const embed = new EmbedBuilder()
                        .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                        .setTitle("🎫 Ticket Closed")
                        .setDescription("Thank you for reaching out.\n\nIf you need help from the staff team in the future, please don't hesitate to open another ticket.")
                        .setColor(Colors.Blurple)
                        .setTimestamp();

                    const row = new ActionRowBuilder<ButtonBuilder>()
                        .addComponents(
                            new ButtonBuilder()
                                .setCustomId(`ticket-close-${interaction.message.channel.id}`)
                                .setStyle(ButtonStyle.Secondary)
                                .setEmoji("🔒")
                                .setLabel("Close ticket")
                                .setDisabled(true)
                        );
                    await interaction.message.edit({ components: [row] });

                    await interaction.message.channel.send({ content: interaction.message.channel.topic?.split(", ").map((u) => `<@${u}>`).join(", "), embeds: [embed] });

                    await interaction.message.channel.edit({
                        name: `closed-${interaction.message.channel.id}`,
                        topic: new Date().toISOString(),
                    });

                    await interaction.reply({ content: "Ticket closed.", flags: MessageFlags.Ephemeral });
                }
            }
        }
    }
}

export const slashCommands: SlashCommandData[] = [
    {
        // @ts-ignore
        data: new SlashCommandBuilder()
            .setName("ticket")
            .setDescription("Ticket commands")
            .setContexts(InteractionContextType.Guild)
            .addSubcommand(s =>
                s.setName("create")
                    .setDescription("Creates a new ticket.")
                    .addStringOption(o =>
                        o.setName("reason")
                            .setDescription("Why are you opening this ticket? Keep this short, send extra details in the created channel.")
                            .setRequired(true)
                    )
            )
            .addSubcommand(s =>
                s.setName("close")
                    .setDescription("Closes a ticket.")
                    .addStringOption(o =>
                        o.setName("ticket-id")
                            .setDescription("The ID of the ticket to close. Assumes the current ticket if ran in a ticket channel.")
                            .setRequired(false)
                    )
            )
            .addSubcommand(s =>
                s.setName("add")
                    .setDescription("Adds a user/role to a ticket.")
                    .addMentionableOption(o =>
                        o.setName("target")
                            .setDescription("The user/role to add.")
                            .setRequired(true)
                    )
                    .addBooleanOption(o =>
                        o.setName("ping")
                            .setDescription("Whether or not to ping the user. Defaults to False.")
                            .setRequired(false)
                    )
                    .addStringOption(o =>
                        o.setName("ticket-id")
                            .setDescription("The ID of the ticket to add a role to. Assumes the current ticket if ran in a ticket channel.")
                            .setRequired(false)
                    )
            )
            .addSubcommand(s =>
                s.setName("remove")
                    .setDescription("Removes a user/role to a ticket.")
                    .addMentionableOption(o =>
                        o.setName("target")
                            .setDescription("The user/role to remove.")
                            .setRequired(true)
                    )
                    .addStringOption(o =>
                        o.setName("ticket-id")
                            .setDescription("The ID of the ticket to remove a role from. Assumes the current ticket if ran in a ticket channel.")
                            .setRequired(false)
                    )
            ),
        async execute(interaction) {
            const subcommand = interaction.options.getSubcommand();
            const config = {
                guild: (await getConfig(zodConfig.ConfigKeys.GUILD)) as zodConfig.Guild,
                categories: (await getConfig(zodConfig.ConfigKeys.CATEGORIES)) as zodConfig.Categories,
                roles: (await getConfig(zodConfig.ConfigKeys.ROLES)) as zodConfig.Roles,
            };

            if (interaction.guild && interaction.guild.id === config.guild.id) {
                const getTicket = async (ticketId: string) => {
                    const channel = await getOrFetchGuildChannel(interaction.guild!.channels, ticketId);

                    if (channel && channel.parentId === config.categories.tickets && channel.name.startsWith("ticket-") && channel.type === ChannelType.GuildText) {
                        return channel;
                    } else {
                        return null;
                    }
                };

                const hasPermissions = async (channel: GuildTextBasedChannel, targetId: string) => {
                    return channel.permissionsFor(targetId)?.has([PermissionsBitField.Flags.ViewChannel, PermissionsBitField.Flags.SendMessages]);
                };

                if (subcommand === "create") {
                    const inputs = {
                        reason: interaction.options.getString("reason", true),
                    }

                    const channel = await interaction.guild.channels.create({
                        name: `ticket-${snowflake.nextId()}`,
                        topic: interaction.user.id,
                        parent: config.categories.tickets,
                        permissionOverwrites: [
                            {
                                id: interaction.guild.roles.everyone,
                                deny: [PermissionsBitField.Flags.ViewChannel, PermissionsBitField.Flags.SendMessages]
                            },
                            {
                                id: config.roles.mod,
                                allow: [PermissionsBitField.Flags.ViewChannel, PermissionsBitField.Flags.SendMessages]
                            },
                            {
                                id: config.roles.helper,
                                allow: [PermissionsBitField.Flags.ViewChannel, PermissionsBitField.Flags.SendMessages]
                            },
                            {
                                id: interaction.user.id,
                                allow: [PermissionsBitField.Flags.ViewChannel, PermissionsBitField.Flags.SendMessages]
                            },
                        ]
                    });
                    await channel.edit({ name: `ticket-${channel.id}` });

                    const embed = new EmbedBuilder()
                        .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                        .setTitle("🎫 Ticket Created")
                        .addFields(
                            {
                                name: "Ticket ID",
                                value: `\`${channel.id}\``,
                                inline: false
                            },
                            {
                                name: "Provided Reason",
                                value: inputs.reason,
                                inline: false
                            },
                        )
                        .setTimestamp()
                        .setFooter(
                            {
                                text: "Please be patient, a staff member will be with you soon!"
                            }
                        )
                        .setColor(Colors.Blurple);

                    const row = new ActionRowBuilder<ButtonBuilder>()
                        .addComponents(
                            new ButtonBuilder()
                                .setCustomId(`ticket-close-${channel.id}`)
                                .setStyle(ButtonStyle.Secondary)
                                .setEmoji("🔒")
                                .setLabel("Close ticket")
                        );

                    const msg = await channel.send({ content: `<@${interaction.user.id}>`, embeds: [embed], components: [row] });
                    await msg.pin();

                    await interaction.reply({ content: `Ticket created: <#${channel.id}>`, flags: MessageFlags.Ephemeral });
                } else if (subcommand === "close") {
                    const inputs = {
                        id: interaction.options.getString("ticket-id", false) ?? interaction.channelId,
                    };

                    const ticket = await getTicket(inputs.id);
                    if (ticket !== null) {
                        const auth = await hasPermissions(ticket, interaction.user.id);

                        if (auth) {
                            const newOverwrites = ticket.permissionOverwrites.cache.map((p) => {
                                if (p.id !== interaction.client.user.id && p.id !== config.roles.helper && p.id !== config.roles.mod && p.id !== interaction.guild!.roles.everyone.id) {
                                    return {
                                        id: p.id,
                                        deny: [PermissionsBitField.Flags.SendMessages],
                                        allow: [PermissionsBitField.Flags.ViewChannel]
                                    };
                                } else {
                                    return p;
                                }
                            });
                            await ticket.permissionOverwrites.set(newOverwrites);

                            const embed = new EmbedBuilder()
                                .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                                .setTitle("🎫 Ticket Closed")
                                .setDescription("Thank you for reaching out.\n\nIf you need help from the staff team in the future, please don't hesitate to open another ticket.")
                                .setColor(Colors.Blurple)
                                .setTimestamp();

                            await ticket.send({ content: ticket.topic?.split(", ").map((u) => `<@${u}>`).join(", "), embeds: [embed] });

                            await ticket.edit({
                                name: `closed-${ticket.id}`,
                                topic: new Date().toISOString(),
                            });

                            await interaction.reply({ content: "Ticket closed.", flags: MessageFlags.Ephemeral });
                        } else {
                            await interaction.reply({ content: `You don't have permissions to close this ticket.`, flags: MessageFlags.Ephemeral });
                        }
                    } else {
                        await interaction.reply({ content: `No open ticket with the ID \`${inputs.id}\` found.`, flags: MessageFlags.Ephemeral });
                    }
                } else if (subcommand === "add") {
                    const inputs = {
                        target: interaction.options.getMentionable("target", true),
                        ping: interaction.options.getBoolean("ping", false) ?? true,
                        id: interaction.options.getString("ticket-id", false) ?? interaction.channelId,
                    };

                    const ticket = await getTicket(inputs.id);

                    if (ticket !== null) {
                        const auth = await hasPermissions(ticket, interaction.user.id);

                        if (auth) {
                            if (inputs.target instanceof GuildMember || inputs.target instanceof Role) {
                                const name = inputs.target instanceof GuildMember ? inputs.target.user.username : inputs.target.name;

                                await ticket.permissionOverwrites.edit(inputs.target.id, { ViewChannel: true, SendMessages: true });

                                const embed = new EmbedBuilder()
                                    .setTitle(`🎫 Added ${inputs.target instanceof GuildMember ? "user" : "role"} ${name} to ticket`)
                                    .setTimestamp()
                                    .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                                    .setColor(Colors.Blurple);

                                await ticket.send({ content: inputs.ping ? `<@${inputs.target.id}>` : undefined, embeds: [embed] });
                                await interaction.reply({ content: "User added.", flags: MessageFlags.Ephemeral });
                            } else {
                                await interaction.reply({ content: `An error occurred.`, flags: MessageFlags.Ephemeral });
                            }
                        } else {
                            await interaction.reply({ content: `You don't have permissions to add users to this ticket.`, flags: MessageFlags.Ephemeral });
                        }
                    } else {
                        await interaction.reply({ content: `No open ticket with the ID \`${inputs.id}\` found.`, flags: MessageFlags.Ephemeral });
                    }
                } else if (subcommand === "remove") {
                    const inputs = {
                        target: interaction.options.getMentionable("target", true),
                        id: interaction.options.getString("ticket-id", false) ?? interaction.channelId,
                    };

                    const ticket = await getTicket(inputs.id);

                    if (ticket !== null) {
                        const auth = await hasPermissions(ticket, interaction.user.id);

                        if (auth) {
                            if (inputs.target instanceof GuildMember || inputs.target instanceof Role) {
                                if (
                                    inputs.target.id !== config.roles.mod && // mod role
                                    inputs.target.id !== config.roles.helper && // helper role
                                    inputs.target.id !== interaction.client.user.id // bot
                                ) {
                                    const name = inputs.target instanceof GuildMember ? inputs.target.user.username : inputs.target.name;

                                    await ticket.permissionOverwrites.delete(inputs.target.id);

                                    const embed = new EmbedBuilder()
                                        .setTitle(`🎫 Removed ${inputs.target instanceof GuildMember ? "user" : "role"} ${name} from ticket`)
                                        .setTimestamp()
                                        .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                                        .setColor(Colors.Blurple);

                                    await ticket.send({ embeds: [embed] });
                                    await interaction.reply({ content: "User added.", flags: MessageFlags.Ephemeral });
                                } else {
                                    await interaction.reply({ content: `The mod role, the helper role, or the bot cannot be removed from the ticket.`, flags: MessageFlags.Ephemeral });
                                }
                            } else {
                                await interaction.reply({ content: `An error occurred.`, flags: MessageFlags.Ephemeral });
                            }
                        } else {
                            await interaction.reply({ content: `You don't have permissions to add users to this ticket.`, flags: MessageFlags.Ephemeral });
                        }
                    } else {
                        await interaction.reply({ content: `No open ticket with the ID \`${inputs.id}\` found.`, flags: MessageFlags.Ephemeral });
                    }
                }
            }
        },
    }
]

export async function setup(client: Client<true>) {
    await ticketClearing(client);
    const ticketClearingId = setInterval(() => ticketClearing(client), 60 * 60 * 1000);

    await ticketInteractionCheck(client);
    const ticketInteractionCheckId = setInterval(() => ticketInteractionCheck(client), 60 * 60 * 1000);

    client.on(Events.InteractionCreate, (interaction) => {
        if (interaction.isButton()) {
            ticketButtonHandler(interaction);
        }
    });

    return { tasks: { clearing: ticketClearingId, interactionCheck: ticketInteractionCheckId } };
}