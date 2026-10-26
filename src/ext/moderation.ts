import * as discord from "discord.js";
import Client, { type ConstantButtonData, type TextCommandData } from "../utils/Client";
import { type SlashCommandData } from "../utils/Client";
import { modAction } from "../db/schema";
import { eq } from "drizzle-orm";

type ModAction = typeof modAction.$inferSelect

const actionNames = {
    "WARN": "Warning",
    "MUTE": "Mute",
    "KICK": "Kick",
    "BAN": "Ban",
};

const actionEmojis = {
    "WARN": "⚠️",
    "MUTE": "🔇",
    "KICK": "👢",
    "BAN": "🔨",
};

const actionColors = {
    "WARN": 0xFFCC4D,
    "MUTE": 0xDD2E44,
    "KICK": 0xC1694F,
    "BAN": 0xF38F0C,
};

const standingPointValues = {
    WARN: 1,
    MUTE: 3,
    KICK: 4,
    BAN: 10,
}

async function buildActionDetails(action: ModAction) {
    const details = [
        `>>> **Type:** ${actionNames[action.type]}`,
        `**Status Points:** ${action.isActive ? `${standingPointValues[action.type]}` : "0"} `,
        `**User:** <@${action.user}> (\`${action.user}\`)`,
        `**Author:** <@${action.author}> (\`${action.author}\`)`,
        `**Reason:** ${action.reason}`,
        `**Proof:** ${!action.proof ? "0 entries" : `${action.proof} entries`}`,
        `**Created:** ${discord.time(action.createdAt, discord.TimestampStyles.FullDateShortTime)} (${discord.time(action.createdAt, discord.TimestampStyles.RelativeTime)})`,
        `**Active:** ${action.isActive ? "Yes" : "No"}`,
    ];
    if (action.isActive && action.expiresAt) {
        details.push(`**Expires:** ${discord.time(action.expiresAt, discord.TimestampStyles.FullDateShortTime)} (${discord.time(action.expiresAt, discord.TimestampStyles.RelativeTime)})`)
    } else if (action.isActive && !action.expiresAt) {
        details.push(`**Expires:** Never`)
    } else if (!action.isActive && action.expiresAt) {
        details.push(`**Expired:** ${discord.time(action.expiresAt, discord.TimestampStyles.FullDateShortTime)} (${discord.time(action.expiresAt, discord.TimestampStyles.RelativeTime)})`)
    }

    const container = new discord.ContainerBuilder()
        .setAccentColor(actionColors[action.type])
        .addTextDisplayComponents(td => td.setContent([
            `# ${actionEmojis[action.type]} Mod Action #${action.id}`,
            ...details,
        ].join("\n")));

    return container;
}

const slashCommands: SlashCommandData[] = [
    {
        // @ts-ignore
        data: new discord.SlashCommandBuilder()
            .setName("profile")
            .setDescription("See all moderation actions on a user in a glance.")
            .addUserOption(opt =>
                opt.setName("user")
                    .setDescription("The user to inspect.")
                    .setRequired(true)
            )
            .addBooleanOption(opt =>
                opt.setName("respond-eph")
                    .setDescription("Whether or not to respond ephemerally. Defaults to True.")
                    .setRequired(false)
            )
            .setContexts(discord.InteractionContextType.Guild)
            .setDefaultMemberPermissions(discord.PermissionFlagsBits.KickMembers),
        async execute(interaction) {
            const client = interaction.client as Client;

            const user = interaction.options.getUser("user", true);
            const respondEph = interaction.options.getBoolean("respond-eph", false) ?? true;

            const actions = await client.db.select().from(modAction).where(eq(modAction.user, user.id));
            const activeActions = actions.filter(a => a.isActive === true);

            const warnings = actions.filter(a => a.type === "WARN");
            const mutes = actions.filter(a => a.type === "MUTE");
            const kicks = actions.filter(a => a.type === "KICK");
            const bans = actions.filter(a => a.type === "BAN");

            const activeWarnings = warnings.filter(a => a.isActive === true);
            const activeMutes = mutes.filter(a => a.isActive === true);
            const activeKicks = kicks.filter(a => a.isActive === true);
            const activeBans = bans.filter(a => a.isActive === true);

            const expiredWarnings = warnings.filter(a => a.isActive === false);
            const expiredMutes = mutes.filter(a => a.isActive === false);
            const expiredKicks = kicks.filter(a => a.isActive === false);
            const expiredBans = bans.filter(a => a.isActive === false);

            const container = new discord.ContainerBuilder()
                .addSectionComponents(s =>
                    s.addTextDisplayComponents(td =>
                        td.setContent([
                            `# <@${user.id}>'s Moderation Profile`,
                            `${actionEmojis.WARN} **${activeWarnings.length} active warning(s)** (${expiredWarnings.length} expired)`,
                            `${actionEmojis.MUTE} **${activeMutes.length} active mute(s)** (${expiredMutes.length} expired)`,
                            `${actionEmojis.KICK} **${activeKicks.length} active kick(s)** (${expiredKicks.length} expired)`,
                            `${actionEmojis.BAN} **${activeBans.length} active bans(s)** (${expiredBans.length} expired)`,
                        ].join("\n"))
                    )
                        .setThumbnailAccessory(tb =>
                            tb.setURL(user.displayAvatarURL())
                        )
                );

            if (actions.length > 0) {
                const mostRecent = actions.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())[0]!;
                container.addSeparatorComponents(s => s.setSpacing(discord.SeparatorSpacingSize.Large));
                container.addSectionComponents(s =>
                    s.addTextDisplayComponents(td =>
                        td.setContent([
                            `## Most Recent Action`,
                            `### ${actionEmojis[mostRecent.type]} ${actionNames[mostRecent.type]} #${mostRecent.id}`,
                            `>>> **Author:** <@${mostRecent.author}>`,
                            `**Reason:** ${mostRecent.reason}`,
                            `**Created:** ${discord.time(mostRecent.createdAt, discord.TimestampStyles.LongDateShortTime)} (${discord.time(mostRecent.createdAt, discord.TimestampStyles.RelativeTime)})`,
                        ].join("\n"))
                    )
                        .setButtonAccessory(
                            new discord.ButtonBuilder()
                                .setCustomId(`latest-${mostRecent.id}`)
                                .setLabel("More Details")
                                .setEmoji(actionEmojis[mostRecent.type])
                                .setStyle(discord.ButtonStyle.Secondary)
                        )
                )
            }

            // determine account standing
            let standingScore = 0;

            // warning    1pt
            standingScore += activeWarnings.length * standingPointValues.WARN;
            // mute       3pts
            standingScore += activeMutes.length * standingPointValues.MUTE;
            // kick       5pts
            standingScore += activeKicks.length * standingPointValues.KICK;
            // ban        10pts
            standingScore += activeBans.length * standingPointValues.BAN;

            // fair       0-4 pts
            // bad        5-9 pts
            // very bad   10-14 pts
            // dangerous  15+ pts

            let standingEmojiName = "";
            let standingColor: number = discord.Colors.Blurple;
            let standing = "";

            if (standingScore < 5) {
                standingEmojiName = "statusFair";
                standingColor = discord.Colors.Green;
                standing = "Fair";
            } else if (standingScore > 4 && standingScore < 10) {
                standingEmojiName = "statusBad";
                standingColor = discord.Colors.Yellow;
                standing = "Bad";
            } else if (standingScore > 9 && standingScore < 15) {
                standingEmojiName = "statusVBad";
                standingColor = discord.Colors.Orange;
                standing = "Very Bad";
            } else if (standingScore > 15) {
                standingEmojiName = "statusDanger";
                standingColor = discord.Colors.Red;
                standing = "Dangerous";
            }

            const standingEmoji = await client.getEmoji(standingEmojiName);

            container.addSeparatorComponents(s => s.setSpacing(discord.SeparatorSpacingSize.Large));
            const standingButton = new discord.ButtonBuilder()
                .setCustomId(`standing-${user.id}`)
                .setLabel("More Details")
                .setStyle(discord.ButtonStyle.Secondary);
            if (standingEmoji) {
                standingButton.setEmoji({
                    id: standingEmoji.id,
                    name: standingEmoji.name,
                    animated: standingEmoji.animated
                });
            }

            if (standingEmoji) {
                container.addSectionComponents(s =>
                    s.addTextDisplayComponents(td =>
                        td.setContent([
                            `## Account Standing`,
                            `<@${user.id}>'s account is in <${standingEmoji.animated ? "a" : ""}:${standingEmoji.name}:${standingEmoji.id}> **${standing}** condition, with ${standingScore} point(s).`
                        ].join("\n"))
                    )
                        .setButtonAccessory(standingButton)
                );
            } else {
                container.addSectionComponents(s =>
                    s.addTextDisplayComponents(td =>
                        td.setContent([
                            `## Account Standing`,
                            `<@${user.id}>'s account is in **${standing}** condition, with ${standingScore} point(s).`
                        ].join("\n"))
                    )
                        .setButtonAccessory(standingButton)
                );
            }
            container.setAccentColor(standingColor);


            container.addSeparatorComponents(s => s.setSpacing(discord.SeparatorSpacingSize.Large));
            container.addActionRowComponents(
                new discord.ActionRowBuilder<discord.ButtonBuilder>()
                    .addComponents(
                        new discord.ButtonBuilder()
                            .setCustomId(`warns-${user.id}`)
                            .setEmoji(actionEmojis.WARN)
                            .setLabel("See all Warnings")
                            .setDisabled(warnings.length <= 0)
                            .setStyle(discord.ButtonStyle.Secondary),
                        new discord.ButtonBuilder()
                            .setCustomId(`mutes-${user.id}`)
                            .setEmoji(actionEmojis.MUTE)
                            .setLabel("See all Mutes")
                            .setDisabled(mutes.length <= 0)
                            .setStyle(discord.ButtonStyle.Secondary),
                        new discord.ButtonBuilder()
                            .setCustomId(`kicks-${user.id}`)
                            .setEmoji(actionEmojis.KICK)
                            .setLabel("See all Kicks")
                            .setDisabled(kicks.length <= 0)
                            .setStyle(discord.ButtonStyle.Secondary),
                        new discord.ButtonBuilder()
                            .setCustomId(`bans-${user.id}`)
                            .setEmoji(actionEmojis.BAN)
                            .setLabel("See all Bans")
                            .setDisabled(bans.length <= 0)
                            .setStyle(discord.ButtonStyle.Secondary),
                    )
            );

            const flags = respondEph
                ? [discord.MessageFlags.IsComponentsV2, discord.MessageFlags.Ephemeral]
                : [discord.MessageFlags.IsComponentsV2];

            const reply = await interaction.reply({
                components: [container],
                // @ts-ignore
                flags,
            });

            const collectorFilter = (i: discord.Interaction) => i.user.id === interaction.user.id;

            function disableAllButtons(container: discord.ContainerBuilder) {
                for (const comp of container.components) {
                    if (comp instanceof discord.ActionRowBuilder) {
                        for (const child of comp.components) {
                            if (child instanceof discord.ButtonBuilder) child.setDisabled(true);
                        }
                    }
                    else if (comp instanceof discord.SectionBuilder && comp.accessory instanceof discord.ButtonBuilder) {
                        comp.accessory.setDisabled(true);
                    }
                }
            }

            const collector = reply.createMessageComponentCollector({ filter: collectorFilter, componentType: discord.ComponentType.Button, time: 1000 * 60 * 5 });

            collector.on("collect", async (i: discord.ButtonInteraction) => {
                if (i.customId.startsWith("latest-")) {
                    const latest = actions.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())[0]!;

                    if (latest) {
                        const c = await buildActionDetails(latest);

                        // @ts-ignore
                        await i.reply({ components: [c], flags });
                    } else {
                        await i.reply({ content: "There has been no moderation actions on this user.", flags: discord.MessageFlags.Ephemeral })
                    }
                } else if (i.customId.startsWith("standing-")) {
                    const activeLines = activeActions.map((action) => {
                        return `- ${actionEmojis[action.type]} A **${actionNames[action.type]}** on ${discord.time(action.createdAt, discord.TimestampStyles.LongDate)} added ${standingPointValues[action.type]} point(s).`
                    });
                    const linesSliced = activeLines.slice(0, 9);
                    const extraLines = activeLines.length - 9;
                    if (extraLines > 0) {
                        linesSliced.push(`- and ${extraLines} more action(s)...`);
                    }
                    if (activeLines.length === 0) {
                        linesSliced.push("No active actions have modified this user's status.");
                    }

                    const c = new discord.ContainerBuilder()
                        .setAccentColor(standingColor)
                        .addTextDisplayComponents(td => td.setContent(`# <@${user.id}>'s Account Status`))
                        .addMediaGalleryComponents(mg =>
                            mg.addItems(mgi => mgi.setURL(`https://bucket-fansbot.valbuilds.xyz/account-status/${standingScore < 15 ? standingScore : '15'}.png`))
                        )
                        .addTextDisplayComponents(td => td.setContent(`<@${user.id}>'s account is in **${standing}** standing, with ${standingScore} point(s).`))
                        .addSeparatorComponents(s => s.setSpacing(discord.SeparatorSpacingSize.Large))
                        .addTextDisplayComponents(td => td.setContent([
                            "## Breakdown",
                            ...linesSliced
                        ].join("\n")));

                    await i.reply({
                        components: [c],
                        // @ts-ignore
                        flags,
                    });
                } else if (i.customId.startsWith("warns-")) {
                    const list = warnings.map((warning) => {
                        return `- #${warning.id} for ${warning.reason}${warning.isActive ? "" : " (expired)"}`
                    });
                    const listSliced = list.slice(0, 9);
                    const extraLines = list.length - 9;
                    if (extraLines > 0) {
                        listSliced.push(`- and ${extraLines} more warning(s)...`);
                    }
                    if (list.length === 0) {
                        listSliced.push("No warnings have been issued to this user.");
                    }

                    const c = new discord.ContainerBuilder()
                        .setAccentColor(actionColors.WARN)
                        .addTextDisplayComponents(td => td.setContent([
                            `# ${actionEmojis.WARN} <@${user.id}>'s Warnings`,
                            ...listSliced,
                        ].join("\n")));

                    // @ts-ignore
                    await i.reply({ components: [c], flags });
                } else if (i.customId.startsWith("mutes-")) {
                    const list = mutes.map((mute) => {
                        return `- #${mute.id} for ${mute.reason}${mute.isActive ? "" : " (expired)"}`
                    });
                    const listSliced = list.slice(0, 9);
                    const extraLines = list.length - 9;
                    if (extraLines > 0) {
                        listSliced.push(`- and ${extraLines} more warning(s)...`);
                    }
                    if (list.length === 0) {
                        listSliced.push("No warnings have been issued to this user.");
                    }

                    const c = new discord.ContainerBuilder()
                        .setAccentColor(actionColors.MUTE)
                        .addTextDisplayComponents(td => td.setContent([
                            `# ${actionEmojis.MUTE} <@${user.id}>'s Warnings`,
                            ...listSliced,
                        ].join("\n")));

                    // @ts-ignore
                    await i.reply({ components: [c], flags });
                } else if (i.customId.startsWith("kicks-")) {
                    const list = kicks.map((kick) => {
                        return `- #${kick.id} for ${kick.reason}${kick.isActive ? "" : " (expired)"}`
                    });
                    const listSliced = list.slice(0, 9);
                    const extraLines = list.length - 9;
                    if (extraLines > 0) {
                        listSliced.push(`- and ${extraLines} more warning(s)...`);
                    }
                    if (list.length === 0) {
                        listSliced.push("No warnings have been issued to this user.");
                    }

                    const c = new discord.ContainerBuilder()
                        .setAccentColor(actionColors.KICK)
                        .addTextDisplayComponents(td => td.setContent([
                            `# ${actionEmojis.KICK} <@${user.id}>'s Warnings`,
                            ...listSliced,
                        ].join("\n")));

                    // @ts-ignore
                    await i.reply({ components: [c], flags });
                } else if (i.customId.startsWith("bans-")) {
                    const list = bans.map((ban) => {
                        return `- #${ban.id} for ${ban.reason}${ban.isActive ? "" : " (expired)"}`
                    });
                    const listSliced = list.slice(0, 9);
                    const extraLines = list.length - 9;
                    if (extraLines > 0) {
                        listSliced.push(`- and ${extraLines} more warning(s)...`);
                    }
                    if (list.length === 0) {
                        listSliced.push("No warnings have been issued to this user.");
                    }

                    const c = new discord.ContainerBuilder()
                        .setAccentColor(actionColors.BAN)
                        .addTextDisplayComponents(td => td.setContent([
                            `# ${actionEmojis.BAN} <@${user.id}>'s Warnings`,
                            ...listSliced,
                        ].join("\n")));

                    // @ts-ignore
                    await i.reply({ components: [c], flags });
                }
            });

            collector.on('end', async (collected) => {
                disableAllButtons(container);
                await interaction
                    .editReply({
                        components: [container],
                        flags: [discord.MessageFlags.IsComponentsV2],
                    })
                    .catch(() => { });
            });
        }
    }
];

const textCommands: TextCommandData[] = [

        await interaction.reply({
            components: [container],
            flags: respondEph
                ? [discord.MessageFlags.IsComponentsV2, discord.MessageFlags.Ephemeral]
                : [discord.MessageFlags.IsComponentsV2],
        });
    }
}
];

const constantButtons: ConstantButtonData[] = [];

export async function setup(client: Client<true>): Promise<void> {
    slashCommands.forEach(data => client.addSlashCommand(data));
    textCommands.forEach(data => client.addTextCommand(data));
    constantButtons.forEach(data => client.addConstantButton(data));

    console.log("Moderation extension loaded.");
    return;
}