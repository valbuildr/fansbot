import type { SlashCommandData } from "../ext";
import { isMod } from "../utils/staffCheck";
import { ActionRowBuilder, AllowedMentionsTypes, ButtonBuilder, ButtonInteraction, ButtonStyle, ChannelType, Colors, ComponentType, EmbedBuilder, EntryPointCommandHandlerType, InteractionContextType, Message, MessageFlags, ModalBuilder, PermissionFlagsBits, SlashCommandBuilder, StringSelectMenuOptionBuilder, TextInputStyle, type GuildTextBasedChannel, type MessageCreateOptions } from "discord.js";
import * as zodSchema from "@fansbot/db/schema/zod";
import db from "@fansbot/db";
import * as schema from "@fansbot/db/schema";
import { Pagination } from "pagination.djs";
import { eq } from "drizzle-orm";

export const slashCommands: SlashCommandData[] = [
    {
        // @ts-ignore
        data: new SlashCommandBuilder()
            .setName("template")
            .setDescription("Message template commands")
            .setContexts(InteractionContextType.Guild)
            .setDefaultMemberPermissions(PermissionFlagsBits.ManageGuild)
            .addSubcommand(s =>
                s.setName("create")
                    .setDescription("Mod: Create a new message template.")
            )
            .addSubcommand(s =>
                s.setName("ls")
                    .setDescription("Mod: List existing message templates.")
                    .addStringOption(o =>
                        o.setName("name")
                            .setDescription("Search by template names.")
                            .setRequired(false)
                    )
            )
            .addSubcommand(s =>
                s.setName("rm")
                    .setDescription("Mod: Delete a message template.")
                    .addStringOption(o =>
                        o.setName("id")
                            .setDescription("The ID of the message template.")
                            .setRequired(true)
                    )
            )
            .addSubcommand(s =>
                s.setName("update")
                    .setDescription("Mod: Update a message template.")
                    .addStringOption(o =>
                        o.setName("id")
                            .setDescription("The ID of the message template.")
                            .setRequired(true)
                    )
            )
            .addSubcommand(s =>
                s.setName("preview")
                    .setDescription("Mod: Preview a message template.")
                    .addStringOption(o =>
                        o.setName("id")
                            .setDescription("The ID of the message template.")
                            .setRequired(true)
                    )
            )
            .addSubcommand(s =>
                s.setName("send")
                    .setDescription("Mod: Send a message template.")
                    .addStringOption(o =>
                        o.setName("id")
                            .setDescription("The ID of the message template.")
                            .setRequired(true)
                    )
                    .addChannelOption(o =>
                        o.setName("channel")
                            .setDescription("The channel to send the template to.")
                            .addChannelTypes(ChannelType.GuildText)
                            .setRequired(true)
                    )
            ),
        async execute(interaction) {
            if (interaction.guild) {
                const auth = await isMod(interaction.member!.roles);

                const subcommand = interaction.options.getSubcommand();

                const messageFmt = (data: zodSchema.MessageData, allowedMentions: string[]): MessageCreateOptions => {
                    const send: MessageCreateOptions = {};

                    if (data.content) {
                        send.content = data.content;
                    }
                    if (data.embeds) {
                        send.embeds = data.embeds.map((e) => {
                            const builder = new EmbedBuilder();

                            if (e.title) {
                                builder.setTitle(e.title);
                            }
                            if (e.description) {
                                builder.setDescription(e.description);
                            }
                            if (e.color) {
                                builder.setColor(e.color);
                            }
                            if (e.author) {
                                builder.setAuthor({
                                    name: e.author.name,
                                    url: e.author.url,
                                    iconURL: e.author.icon_url,
                                });
                            }
                            if (e.fields) {
                                e.fields.forEach((f) => {
                                    builder.addFields(
                                        {
                                            name: f.name,
                                            value: f.value,
                                            inline: f.inline,
                                        }
                                    )
                                })
                            }
                            if (e.footer) {
                                builder.setFooter({ text: e.footer.text, iconURL: e.footer.icon_url })
                            }
                            if (e.timestamp) {
                                builder.setTimestamp(new Date(e.timestamp));
                            }
                            if (e.image) {
                                builder.setImage(e.image.url);
                            }
                            if (e.thumbnail) {
                                builder.setImage(e.thumbnail.url);
                            }

                            return builder;
                        })
                    }
                    if (data.components) {
                        send.components = data.components.map((r) => {
                            const row = new ActionRowBuilder<ButtonBuilder>();

                            r.components.forEach((b) => {
                                const builder = new ButtonBuilder()
                                    .setStyle(ButtonStyle.Link)
                                    .setURL(b.url);

                                if (b.label) {
                                    builder.setLabel(b.label);
                                }
                                if (b.emoji) {
                                    builder.setEmoji({
                                        id: b.emoji.id,
                                        name: b.emoji.name,
                                        animated: b.emoji.animated,
                                    });
                                }
                                if (b.disabled !== undefined) {
                                    builder.setDisabled(b.disabled);
                                }

                                row.addComponents(builder);
                            })

                            return row;
                        })
                    }

                    send.allowedMentions = {
                        parse: [...allowedMentions] as AllowedMentionsTypes[]
                    }

                    return send;
                };

                if (auth === true) {
                    if (subcommand === "create") {
                        const modal = new ModalBuilder()
                            .setCustomId("create-template")
                            .setTitle("Create New Template")
                            .addLabelComponents(l =>
                                l.setLabel("Name")
                                    .setDescription("The name of the template, for searching.")
                                    .setTextInputComponent(c =>
                                        c.setCustomId("name")
                                            .setMinLength(3)
                                            .setMaxLength(512)
                                            .setStyle(TextInputStyle.Short)
                                            .setRequired(true)
                                    )
                            )
                            .addLabelComponents(l =>
                                l.setLabel("Message JSON")
                                    .setDescription("The data for the message. Generate the JSON data on Discohook. (https://discohook.app)")
                                    .setTextInputComponent(c =>
                                        c.setCustomId("json")
                                            .setStyle(TextInputStyle.Paragraph)
                                            .setRequired(true)
                                    )
                            )
                            .addLabelComponents(l =>
                                l.setLabel("Allowed Mentions")
                                    .setDescription("What mentions to allow when sending the message. Can be overrided if needed.")
                                    .setStringSelectMenuComponent(c =>
                                        c.setCustomId("allowed-mentions")
                                            .setPlaceholder("Leave blank to allow no mentions.")
                                            .setMaxValues(3)
                                            .setRequired(false)
                                            .addOptions(
                                                new StringSelectMenuOptionBuilder()
                                                    .setLabel("Everyone")
                                                    .setDescription("Allow @everyone and @here mentions.")
                                                    .setValue("everyone"),
                                                new StringSelectMenuOptionBuilder()
                                                    .setLabel("Roles")
                                                    .setDescription("Allow role mentions.")
                                                    .setValue("roles"),
                                                new StringSelectMenuOptionBuilder()
                                                    .setLabel("Users")
                                                    .setDescription("Allow user mentions.")
                                                    .setValue("users"),
                                            )
                                    )
                            );

                        await interaction.showModal(modal);

                        interaction.awaitModalSubmit({ time: 60_000 })
                            .then(async (i) => {
                                await i.deferReply({ flags: MessageFlags.Ephemeral });

                                const inputs = {
                                    name: i.fields.getTextInputValue("name"),
                                    json: i.fields.getTextInputValue("json"),
                                    allowedMentions: i.fields.getStringSelectValues("allowed-mentions"),
                                };

                                let parsed: string | undefined;
                                try {
                                    parsed = JSON.parse(inputs.json);
                                } catch {
                                    await i.editReply({ content: "JSON parsing error. Please try again." });
                                    return;
                                }

                                const parseResult = zodSchema.MessageDataSchema.safeParse(parsed);

                                if (parseResult.success) {
                                    // @ts-ignore
                                    const entry = await db.insert(schema.template).values({
                                        name: inputs.name,
                                        data: parseResult.data!,
                                        allowedMentions: inputs.allowedMentions,
                                    }).returning();

                                    const embed = new EmbedBuilder()
                                        .setAuthor({ name: i.user.username, iconURL: i.user.avatarURL() ?? i.guild!.iconURL()! })
                                        .setTitle("✅ Message Template Created")
                                        .setColor(Colors.Green)
                                        .setDescription("Use `/template preview` to preview it.")
                                        .addFields(
                                            { name: "ID", value: `\`${entry[0]!.id}\`` }
                                        )
                                        .setTimestamp();

                                    await i.editReply({ embeds: [embed] });
                                } else {
                                    await i.editReply({ content: "Please provide valid JSON message data.\nUse [Discohook](<https://discohook.app>) to generate it.\n-# JSON message data can be found in Options > JSON Editor." })
                                }
                            })
                    } else if (subcommand === "ls") {
                        const inputs = {
                            name: interaction.options.getString("name", false)
                        };

                        let entries = await db.query.template.findMany();

                        if (inputs.name) {
                            entries = entries.filter((e) => e.name.includes(inputs.name!));
                        }

                        if (entries.length === 0) {
                            await interaction.reply("No entries match the selected filters.");
                            return;
                        } else {
                            new Pagination(interaction, { limit: 10 })
                                .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                                .setTitle("🔍 Message Template Query")
                                .setColor(Colors.Blue)
                                .setFields(entries.map((en) => {
                                    return {
                                        name: `${en.name} (\`${en.id}\`)`,
                                        value: [
                                            `>>> **Content Length:** ${en.data.content ? en.data.content.length : 0}`,
                                            `**Embeds:** ${en.data.embeds ? en.data.embeds.length : 0}`,
                                            `**Component Rows:** ${en.data.components ? en.data.components.length : 0}`,
                                            `**Allowed Mentions:** ${(en.allowedMentions && en.allowedMentions.length !== 0) ? en.allowedMentions.map((a) => a.charAt(0).toUpperCase() + a.slice(1)).join(", ") : "None"}`,
                                        ].join("\n")
                                    }
                                }))
                                .paginateFields(true)
                                .setAuthorizedUsers([interaction.user.id])
                                .setTimestamp()
                                .render();
                        }
                    } else if (subcommand === "rm") {
                        const inputs = {
                            id: interaction.options.getString("id", true)
                        };

                        const query = await db.query.template.findFirst({
                            where: eq(schema.template.id, inputs.id)
                        });

                        if (query) {
                            const e = new EmbedBuilder()
                                .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                                .setTitle("🗑️ Delete Message Template?")
                                .setColor(Colors.Red)
                                .setTimestamp()
                                .setFields(
                                    {
                                        name: "Name",
                                        value: query.name,
                                        inline: true
                                    },
                                    {
                                        name: "Content Length",
                                        value: (query.data.content ? query.data.content.length : 0).toString(),
                                        inline: true
                                    },
                                    {
                                        name: "Embeds",
                                        value: (query.data.embeds ? query.data.embeds.length : 0).toString(),
                                        inline: true
                                    },
                                    {
                                        name: "Component Rows",
                                        value: (query.data.components ? query.data.components.length : 0).toString(),
                                        inline: true
                                    },
                                    {
                                        name: "Allowed Mentions",
                                        value: (query.allowedMentions && query.allowedMentions.length !== 0) ? query.allowedMentions.map((a) => a.charAt(0).toUpperCase() + a.slice(1)).join(", ") : "None",
                                        inline: true
                                    },
                                );

                            const a = new ActionRowBuilder<ButtonBuilder>()
                                .addComponents(
                                    new ButtonBuilder()
                                        .setCustomId("delete")
                                        .setLabel("Delete")
                                        .setStyle(ButtonStyle.Danger),
                                    new ButtonBuilder()
                                        .setCustomId("cancel")
                                        .setLabel("Cancel")
                                        .setStyle(ButtonStyle.Secondary)
                                );

                            const reply = await interaction.reply({ embeds: [e], components: [a] });

                            const collectorFilter = (i: ButtonInteraction) => {
                                i.deferUpdate();
                                return i.user.id === interaction.user.id;
                            }

                            const disableAllButtons = async (msg: Message) => {
                                const newActionRow = new ActionRowBuilder<ButtonBuilder>()
                                    .addComponents(
                                        new ButtonBuilder()
                                            .setCustomId("delete")
                                            .setLabel("Delete")
                                            .setStyle(ButtonStyle.Danger)
                                            .setDisabled(true),
                                        new ButtonBuilder()
                                            .setCustomId("cancel")
                                            .setLabel("Cancel")
                                            .setStyle(ButtonStyle.Secondary)
                                            .setDisabled(true)
                                    );

                                await msg.edit({ embeds: [e], components: [newActionRow] })
                            }

                            const collector = reply.createMessageComponentCollector({ componentType: ComponentType.Button, time: 15_000 });

                            collector.on('collect', async (i) => {
                                if (collectorFilter(i)) {
                                    if (i.customId === "delete") {
                                        await db.delete(schema.template).where(eq(schema.template.id, inputs.id));

                                        await disableAllButtons(i.message);

                                        await i.followUp({ content: "Template successfully deleted." });
                                    } else if (i.customId === "cancel") {
                                        await disableAllButtons(i.message);

                                        await i.followUp({ content: "Action cancelled. Nothing was changed." })
                                    }
                                } else {
                                    await i.followUp({ content: "You aren't allowed to interact with this message.", flags: MessageFlags.Ephemeral })
                                }
                            });

                            collector.on('end', async (collected) => {
                                await disableAllButtons(await reply.fetch());
                                if (collected.size === 0) {
                                    await interaction.followUp({ content: "Timed out. Please try again." });
                                }
                            })
                        } else {
                            await interaction.reply({ content: `No template with the ID \`${inputs.id}\` found.`, flags: MessageFlags.Ephemeral });
                        }
                    } else if (subcommand === "update") {
                        const inputs = {
                            id: interaction.options.getString("id", true)
                        };

                        const query = await db.query.template.findFirst({
                            where: eq(schema.template.id, inputs.id)
                        });

                        if (query) {
                            const modal = new ModalBuilder()
                                .setCustomId("update-template")
                                .setTitle("Update Template")
                                .addLabelComponents(l =>
                                    l.setLabel("Name")
                                        .setDescription("The name of the template, for searching.")
                                        .setTextInputComponent(c =>
                                            c.setCustomId("name")
                                                .setMinLength(3)
                                                .setMaxLength(512)
                                                .setStyle(TextInputStyle.Short)
                                                .setRequired(true)
                                                .setValue(query.name)
                                        )
                                )
                                .addLabelComponents(l =>
                                    l.setLabel("Message JSON")
                                        .setDescription("The data for the message. Generate the JSON data on Discohook. (https://discohook.app)")
                                        .setTextInputComponent(c =>
                                            c.setCustomId("json")
                                                .setStyle(TextInputStyle.Paragraph)
                                                .setRequired(true)
                                                .setValue(JSON.stringify(query.data, null, 4))
                                        )
                                )
                                .addLabelComponents(l =>
                                    l.setLabel("Allowed Mentions")
                                        .setDescription("What mentions to allow when sending the message. Can be overrided if needed.")
                                        .setStringSelectMenuComponent(c =>
                                            c.setCustomId("allowed-mentions")
                                                .setPlaceholder("Leave blank to allow no mentions.")
                                                .setMaxValues(3)
                                                .setRequired(false)
                                                .addOptions(
                                                    new StringSelectMenuOptionBuilder()
                                                        .setLabel("Everyone")
                                                        .setDescription("Allow @everyone and @here mentions.")
                                                        .setValue("everyone")
                                                        .setDefault(query.allowedMentions?.includes("everyone")),
                                                    new StringSelectMenuOptionBuilder()
                                                        .setLabel("Roles")
                                                        .setDescription("Allow role mentions.")
                                                        .setValue("roles")
                                                        .setDefault(query.allowedMentions?.includes("roles")),
                                                    new StringSelectMenuOptionBuilder()
                                                        .setLabel("Users")
                                                        .setDescription("Allow user mentions.")
                                                        .setValue("users")
                                                        .setDefault(query.allowedMentions?.includes("users")),
                                                )
                                        )
                                );

                            await interaction.showModal(modal);

                            interaction.awaitModalSubmit({ time: 60_000 })
                                .then(async (i) => {
                                    await i.deferReply({ flags: MessageFlags.Ephemeral });

                                    const modalInputs = {
                                        name: i.fields.getTextInputValue("name"),
                                        json: i.fields.getTextInputValue("json"),
                                        allowedMentions: i.fields.getStringSelectValues("allowed-mentions"),
                                    };

                                    let parsed: string | undefined;
                                    try {
                                        parsed = JSON.parse(modalInputs.json);
                                    } catch {
                                        await i.editReply({ content: "JSON parsing error. Please try again." });
                                        return;
                                    }

                                    const parseResult = zodSchema.MessageDataSchema.safeParse(parsed);

                                    if (parseResult.success) {
                                        type Template = typeof schema.template.$inferSelect;
                                        // @ts-ignore
                                        const set: Template = {};

                                        if (modalInputs.name !== query.name) {
                                            set.name = modalInputs.name;
                                        }
                                        if (parseResult.data !== query.data) {
                                            set.data = parseResult.data;
                                        }
                                        if (modalInputs.allowedMentions !== query.allowedMentions) {
                                            set.allowedMentions = modalInputs.allowedMentions as string[];
                                        }

                                        const entry = await db.update(schema.template).set(set).where(eq(schema.template.id, inputs.id)).returning();

                                        const embed = new EmbedBuilder()
                                            .setAuthor({ name: i.user.username, iconURL: i.user.avatarURL() ?? i.guild!.iconURL()! })
                                            .setTitle("✏️ Updated Template")
                                            .setColor(Colors.Yellow)
                                            .setTimestamp()
                                            .addFields(
                                                {
                                                    name: "Before",
                                                    value: [
                                                        `>>> **Name:** ${query.name}`,
                                                        `**Content Length:** ${(query.data.content ? query.data.content.length : 0).toString()}`,
                                                        `**Embeds:** ${(query.data.embeds ? query.data.embeds.length : 0).toString()}`,
                                                        `**Component Rows:** ${(query.data.components ? query.data.components.length : 0).toString()}`,
                                                        `**Allowed Mentions:** ${(query.allowedMentions && query.allowedMentions.length !== 0) ? query.allowedMentions.map((a) => a.charAt(0).toUpperCase() + a.slice(1)).join(", ") : "None"}`
                                                    ].join("\n"),
                                                    inline: true
                                                },
                                                {
                                                    name: "After",
                                                    value: [
                                                        `>>> **Name:** ${entry[0]!.name}`,
                                                        `**Content Length:** ${(entry[0]!.data.content ? entry[0]!.data.content.length : 0).toString()}`,
                                                        `**Embeds:** ${(entry[0]!.data.embeds ? entry[0]!.data.embeds.length : 0).toString()}`,
                                                        `**Component Rows:** ${(entry[0]!.data.components ? entry[0]!.data.components.length : 0).toString()}`,
                                                        `**Allowed Mentions:** ${(entry[0]!.allowedMentions && entry[0]!.allowedMentions.length !== 0) ? entry[0]!.allowedMentions.map((a) => a.charAt(0).toUpperCase() + a.slice(1)).join(", ") : "None"}`
                                                    ].join("\n"),
                                                    inline: true
                                                },
                                            );

                                        await i.editReply({ embeds: [embed] });
                                    } else {
                                        await i.editReply({ content: "Please provide valid JSON message data.\nUse [Discohook](<https://discohook.app>) to generate it.\n-# JSON message data can be found in Options > JSON Editor." })
                                    }
                                })
                        } else {
                            await interaction.reply({ content: `No template with the ID \`${inputs.id}\` found.`, flags: MessageFlags.Ephemeral });
                        }
                    } else if (subcommand === "preview") {
                        const inputs = {
                            id: interaction.options.getString("id", true)
                        };

                        const query = await db.query.template.findFirst({
                            where: eq(schema.template.id, inputs.id)
                        });

                        if (query) {
                            const msgData = messageFmt(query.data, query.allowedMentions);
                            await interaction.reply({ ...msgData, flags: MessageFlags.Ephemeral });
                        } else {
                            await interaction.reply({ content: `No template with the ID \`${inputs.id}\` found.`, flags: MessageFlags.Ephemeral });
                        }
                    } else if (subcommand === "send") {
                        const inputs = {
                            id: interaction.options.getString("id", true),
                            channel: interaction.options.getChannel("channel", true) as GuildTextBasedChannel,
                        };

                        const query = await db.query.template.findFirst({
                            where: eq(schema.template.id, inputs.id)
                        });

                        if (query) {
                            const msg = messageFmt(query.data, query.allowedMentions);
                            const sent = await inputs.channel.send(msg);
                            await interaction.reply({ content: `Message sent! ${sent.url}`, flags: MessageFlags.Ephemeral });
                        } else {
                            await interaction.reply({ content: `No template with the ID \`${inputs.id}\` found.`, flags: MessageFlags.Ephemeral });
                        }
                    }
                } else {
                    await interaction.reply({ content: "You must be a moderator to use this command.", flags: MessageFlags.Ephemeral });
                    return;
                }
            }
        },
    }
];