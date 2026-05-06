import Client from "@/utils/Client";
import type { SlashCommandData } from "@/utils/commandTypes";
import db from "@/db";
import * as schema from "@/db/schema";
import { ActionRowBuilder, ActivityType, ButtonBuilder, ButtonInteraction, ButtonStyle, Colors, ComponentType, EmbedBuilder, GuildMember, InteractionContextType, Message, MessageFlags, SlashCommandBuilder } from "discord.js";
import { isMod } from "@/utils/staffCheck";
import { eq } from "drizzle-orm";

function statusTask(client: Client<true>) {
    client.database.select().from(schema.status)
        .then((entries) => {
            if (entries.length !== 0) {
                const chosen = entries[Math.floor(Math.random() * entries.length)];

                if (chosen) {
                    client.user.setActivity(chosen.name, {
                        type: (() => {
                            switch (chosen.type) {
                                case "competing": return ActivityType.Competing;
                                case "listening": return ActivityType.Listening;
                                case "streaming": return ActivityType.Streaming;
                                case "watching": return ActivityType.Watching;
                                default: return ActivityType.Playing;
                            }
                        })()
                    })
                }
            }

            return;
        })
}

export const slashCommands: SlashCommandData[] = [
    {
        // @ts-ignore
        data: new SlashCommandBuilder()
            .setName("status")
            .setDescription("Status management")
            .setContexts(InteractionContextType.Guild)
            .addSubcommand(s =>
                s.setName("create")
                    .setDescription("Mod: Create a new status entry.")
                    .addStringOption(o =>
                        o.setName("type")
                            .setDescription("The activity's name.")
                            .addChoices(
                                { name: "Competing in", value: "competing" },
                                { name: "Listening to", value: "listening" },
                                { name: "Playing", value: "playing" },
                                { name: "Streaming", value: "streaming" },
                                { name: "Watching", value: "watching" },
                            )
                            .setRequired(true)
                    )
                    .addStringOption(o =>
                        o.setName("name")
                            .setDescription("The activity's name.")
                            .setRequired(true)
                    )
            )
            .addSubcommand(s =>
                s.setName("ls")
                    .setDescription("Mod: Search through status entries.")
                    .addStringOption(o =>
                        o.setName("type")
                            .setDescription("Filter by activity name.")
                            .addChoices(
                                { name: "Competing in", value: "competing" },
                                { name: "Listening to", value: "listening" },
                                { name: "Playing", value: "playing" },
                                { name: "Streaming", value: "streaming" },
                                { name: "Watching", value: "watching" },
                            )
                            .setRequired(false)
                    )
                    .addStringOption(o =>
                        o.setName("name")
                            .setDescription("Filter by activity name.")
                            .setRequired(false)
                    )
            )
            .addSubcommand(s =>
                s.setName("update")
                    .setDescription("Mod: Edit a status entry.")
                    .addStringOption(o =>
                        o.setName("id")
                            .setDescription("The activity's ID.")
                            .setRequired(true)
                    )
                    .addStringOption(o =>
                        o.setName("type")
                            .setDescription("The new activity name.")
                            .addChoices(
                                { name: "Competing in", value: "competing" },
                                { name: "Listening to", value: "listening" },
                                { name: "Playing", value: "playing" },
                                { name: "Streaming", value: "streaming" },
                                { name: "Watching", value: "watching" },
                            )
                            .setRequired(false)
                    )
                    .addStringOption(o =>
                        o.setName("name")
                            .setDescription("The new activity name.")
                            .setRequired(false)
                    )
            )
            .addSubcommand(s =>
                s.setName("rm")
                    .setDescription("Mod: Delete a status entry.")
                    .addStringOption(o =>
                        o.setName("id")
                            .setDescription("The activity's ID.")
                            .setRequired(true)
                    )
            ),
        async execute(interaction) {
            if (interaction.guild) {
                const auth = isMod(interaction.member as GuildMember);

                if (!auth) {
                    await interaction.reply({ content: "You must be a moderator to use this command.", flags: MessageFlags.Ephemeral });
                    return;
                }

                const subcommand = interaction.options.getSubcommand();

                const fullDisplay = (name: string, type: "competing" | "listening" | "playing" | "streaming" | "watching") => {
                    switch (type) {
                        case "competing": return `Competing in ${name}`;
                        case "listening": return `Listening to ${name}`;
                        case "streaming": return `Streaming ${name}`;
                        case "watching": return `Watching ${name}`;
                        default: return `Playing ${name}`;
                    }
                };

                const typeDisplay = (type: "competing" | "listening" | "playing" | "streaming" | "watching") => {
                    switch (type) {
                        case "competing": return `Competing`;
                        case "listening": return `Listening`;
                        case "streaming": return `Streaming`;
                        case "watching": return `Watching`;
                        default: return `Playing`;
                    }
                };

                if (subcommand === "create") {
                    const inputs = {
                        type: interaction.options.getString("type", true) as "competing" | "listening" | "playing" | "streaming" | "watching",
                        name: interaction.options.getString("name", true)
                    }

                    const i = await db.insert(schema.status).values({ name: inputs.name, type: inputs.type }).returning();

                    const e = new EmbedBuilder()
                        .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                        .setTitle("✅ Status Entry Created")
                        .addFields(
                            { name: "ID", value: `\`${i[0]?.id}\``, inline: false },
                            { name: "Type", value: `${typeDisplay(i[0]?.type ?? "playing")}`, inline: false },
                            { name: "Name", value: `${i[0]?.name ?? ""}`, inline: false },
                            { name: "Displayed as", value: `${fullDisplay(i[0]?.name ?? "", i[0]?.type ?? "playing")}`, inline: false },
                        )
                        .setColor(Colors.Green);
                    await interaction.reply({ embeds: [e] });
                } else if (subcommand === "ls") {
                    const inputs = {
                        type: interaction.options.getString("type", false) as "competing" | "listening" | "playing" | "streaming" | "watching",
                        name: interaction.options.getString("name", false)
                    };

                    let q = await db.select().from(schema.status);

                    if (inputs.type) {
                        q = q.filter((e) => e.type === inputs.type);
                    }
                    if (inputs.name) {
                        q = q.filter((e) => e.name.includes(inputs.name!));
                    }

                    const e = new EmbedBuilder()
                        .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                        .setTitle("🔍 Status Entry Query")
                        .setColor(Colors.Blue);

                    q.forEach((en) => {
                        e.addFields(
                            {
                                name: `\`${en.id}\``,
                                value: fullDisplay(en.name, en.type),
                                inline: false
                            }
                        )
                    });

                    if (q.length === 0) {
                        e.setDescription("No entries match the selected filters.");
                    }

                    e.setFooter(
                        { text: `${q.length} entries found` }
                    )

                    await interaction.reply({ embeds: [e] });
                } else if (subcommand === "update") {
                    const inputs = {
                        id: interaction.options.getString("id", true),
                        type: interaction.options.getString("type", false) as "competing" | "listening" | "playing" | "streaming" | "watching",
                        name: interaction.options.getString("name", false)
                    }

                    let set = {};

                    // @ts-ignore
                    if (inputs.type) { set["type"] = inputs.type; }
                    // @ts-ignore
                    if (inputs.name) { set["name"] = inputs.name; }

                    const q = await db.select().from(schema.status).where(eq(schema.status.id, inputs.id));
                    const u = await db.update(schema.status).set(set).where(eq(schema.status.id, inputs.id)).returning();

                    if (q.length === 0) {
                        await interaction.reply({ content: `No status entry with ID \`${inputs.id}\` found.`, flags: MessageFlags.Ephemeral });
                    } else {
                        const e = new EmbedBuilder()
                            .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                            .setTitle("✏️ Status Entry Updated")
                            .setColor(Colors.Yellow)
                            .addFields(
                                { name: "Old Name", value: q[0]?.name ?? "", inline: true },
                                { name: "Old Type", value: typeDisplay(q[0]?.type ?? "playing"), inline: true },
                                { name: "Old Name", value: fullDisplay(q[0]?.name ?? "", q[0]?.type ?? "playing"), inline: true },
                                { name: "New Name", value: u[0]?.name ?? "", inline: true },
                                { name: "New Type", value: typeDisplay(u[0]?.type ?? "playing"), inline: true },
                                { name: "New Name", value: fullDisplay(u[0]?.name ?? "", u[0]?.type ?? "playing"), inline: true },
                            );

                        await interaction.reply({ embeds: [e] });
                    }
                } else if (subcommand === "rm") {
                    const inputs = {
                        id: interaction.options.getString("id", true)
                    }

                    const q = await db.select().from(schema.status).where(eq(schema.status.id, inputs.id));

                    if (q.length === 0) {
                        await interaction.reply({ content: `No status entry with the ID \`${inputs.id}\` found.`, flags: MessageFlags.Ephemeral });
                    } else {
                        const e = new EmbedBuilder()
                            .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() ?? interaction.guild.iconURL()! })
                            .setTitle("🗑️ Delete Status Entry?")
                            .setColor(Colors.Red)
                            .addFields(
                                { name: "Type", value: typeDisplay(q[0]?.type ?? "playing"), inline: false },
                                { name: "Name", value: q[0]?.name ?? "", inline: false },
                                { name: "Displayed as", value: fullDisplay(q[0]?.name ?? "", q[0]?.type ?? "playing"), inline: false },
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
                            )

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
                                    await db.delete(schema.status).where(eq(schema.status.id, inputs.id));

                                    await disableAllButtons(i.message);

                                    await i.followUp({ content: "Entry successfully deleted." });
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
                    }
                }
            }
        },
    }
];

export function setup(client: Client<true>) {
    statusTask(client)
    const statusTaskId = setInterval(() => statusTask(client), 120 * 1000);

    return { tasks: { status: statusTaskId } };
};