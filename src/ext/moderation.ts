import * as discord from "discord.js";
import Client, { type ConstantButtonData, type TextCommandData } from "../utils/Client";
import { type SlashCommandData } from "../utils/Client";
import { modAction } from "../db/schema";
import { eq } from "drizzle-orm";

type ModAction = typeof modAction.$inferSelect

const ACTION_NAMES = {
    "WARN": "Warning",
    "MUTE": "Mute",
    "KICK": "Kick",
    "BAN": "Ban",
};

const ACTIONS_EMOJIS = {
    "WARN": "⚠️",
    "MUTE": "🔇",
    "KICK": "👢",
    "BAN": "🔨",
};

const ACTION_COLORS = {
    "WARN": 0xFFCC4D,
    "MUTE": 0xDD2E44,
    "KICK": 0xC1694F,
    "BAN": 0xF38F0C,
};

const STANDING_POINT_VALUES = {
    WARN: 1,
    MUTE: 3,
    KICK: 4,
    BAN: 10,
};

const STANDING_EMOJIS = {
    FAIR: "statusFair",
    BAD: "statusBad",
    VERY_BAD: "statusVBad",
    DANGEROUS: "statusDanger",
};

const STANDING_COLORS = {
    FAIR: discord.Colors.Green,
    BAD: discord.Colors.Yellow,
    VERY_BAD: discord.Colors.Orange,
    DANGEROUS: discord.Colors.Red,
};

const STANDING_NAMES = {
    FAIR: "Fair",
    BAD: "Bad",
    VERY_BAD: "Very Bad",
    DANGEROUS: "Dangerous",
};

async function fetchAccountStatus(client: Client, userId: string): Promise<{
    status: "FAIR" | "BAD" | "VERY_BAD" | "DANGEROUS" | null;
    points: number;
}> {
    const db = await client.db.select().from(modAction).where(eq(modAction.user, userId));

    let points = 0;
    db.forEach((action) => {
        points += STANDING_POINT_VALUES[action.type] * Number(action.pointMultiplier);
    });
    points = Math.round(points);

    let status: "FAIR" | "BAD" | "VERY_BAD" | "DANGEROUS" | null = null

    if (points <= 4) status = "FAIR";
    if (points >= 5 && points <= 9) status = "BAD";
    if (points >= 10 && points <= 14) status = "VERY_BAD";
    if (points >= 15) status = "DANGEROUS";

    return { status, points };
}

function calculateAccountStatus(actions: ModAction[]): {
    status: "FAIR" | "BAD" | "VERY_BAD" | "DANGEROUS" | null;
    points: number;
} {
    let points = 0;
    actions.forEach((action) => {
        points += STANDING_POINT_VALUES[action.type] * Number(action.pointMultiplier);
    });
    points = Math.round(points);

    let status: "FAIR" | "BAD" | "VERY_BAD" | "DANGEROUS" | null = null

    if (points <= 4) status = "FAIR";
    if (points >= 5 && points <= 9) status = "BAD";
    if (points >= 10 && points <= 14) status = "VERY_BAD";
    if (points >= 15) status = "DANGEROUS";

    return { status, points };
}

async function buildActionDetails(action: ModAction) {
    const details = [
        `>>> **Type:** ${ACTION_NAMES[action.type]}`,
        `**Status Points:** ${action.isActive ? `${STANDING_POINT_VALUES[action.type]}` : "0"} `,
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
        .setAccentColor(ACTION_COLORS[action.type])
        .addTextDisplayComponents(td => td.setContent([
            `# ${ACTIONS_EMOJIS[action.type]} Mod Action #${action.id}`,
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
                            `${ACTIONS_EMOJIS.WARN} **${activeWarnings.length} active warning(s)** (${expiredWarnings.length} expired)`,
                            `${ACTIONS_EMOJIS.MUTE} **${activeMutes.length} active mute(s)** (${expiredMutes.length} expired)`,
                            `${ACTIONS_EMOJIS.KICK} **${activeKicks.length} active kick(s)** (${expiredKicks.length} expired)`,
                            `${ACTIONS_EMOJIS.BAN} **${activeBans.length} active bans(s)** (${expiredBans.length} expired)`,
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
                            `### ${ACTIONS_EMOJIS[mostRecent.type]} ${ACTION_NAMES[mostRecent.type]} #${mostRecent.id}`,
                            `>>> **Author:** <@${mostRecent.author}>`,
                            `**Reason:** ${mostRecent.reason}`,
                            `**Created:** ${discord.time(mostRecent.createdAt, discord.TimestampStyles.LongDateShortTime)} (${discord.time(mostRecent.createdAt, discord.TimestampStyles.RelativeTime)})`,
                        ].join("\n"))
                    )
                        .setButtonAccessory(
                            new discord.ButtonBuilder()
                                .setCustomId(`latest-${mostRecent.id}`)
                                .setLabel("More Details")
                                .setEmoji(ACTIONS_EMOJIS[mostRecent.type])
                                .setStyle(discord.ButtonStyle.Secondary)
                        )
                )
            }

            const standing = await fetchAccountStatus(client, user.id);

            const standingEmoji = await client.getEmoji(STANDING_EMOJIS[standing.status!]);

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
                            `<@${user.id}>'s account is in <${standingEmoji.animated ? "a" : ""}:${standingEmoji.name}:${standingEmoji.id}> **${STANDING_NAMES[standing.status!]}** condition, with ${standing.points} point(s).`
                        ].join("\n"))
                    )
                        .setButtonAccessory(standingButton)
                );
            } else {
                container.addSectionComponents(s =>
                    s.addTextDisplayComponents(td =>
                        td.setContent([
                            `## Account Standing`,
                            `<@${user.id}>'s account is in **${STANDING_NAMES[standing.status!]}** condition, with ${standing.points} point(s).`
                        ].join("\n"))
                    )
                        .setButtonAccessory(standingButton)
                );
            }
            container.setAccentColor(STANDING_COLORS[standing.status!]);


            container.addSeparatorComponents(s => s.setSpacing(discord.SeparatorSpacingSize.Large));
            container.addActionRowComponents(
                new discord.ActionRowBuilder<discord.ButtonBuilder>()
                    .addComponents(
                        new discord.ButtonBuilder()
                            .setCustomId(`warns-${user.id}`)
                            .setEmoji(ACTIONS_EMOJIS.WARN)
                            .setLabel("See all Warnings")
                            .setDisabled(warnings.length <= 0)
                            .setStyle(discord.ButtonStyle.Secondary),
                        new discord.ButtonBuilder()
                            .setCustomId(`mutes-${user.id}`)
                            .setEmoji(ACTIONS_EMOJIS.MUTE)
                            .setLabel("See all Mutes")
                            .setDisabled(mutes.length <= 0)
                            .setStyle(discord.ButtonStyle.Secondary),
                        new discord.ButtonBuilder()
                            .setCustomId(`kicks-${user.id}`)
                            .setEmoji(ACTIONS_EMOJIS.KICK)
                            .setLabel("See all Kicks")
                            .setDisabled(kicks.length <= 0)
                            .setStyle(discord.ButtonStyle.Secondary),
                        new discord.ButtonBuilder()
                            .setCustomId(`bans-${user.id}`)
                            .setEmoji(ACTIONS_EMOJIS.BAN)
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
                        return `- ${ACTIONS_EMOJIS[action.type]} A **${ACTION_NAMES[action.type]}** on ${discord.time(action.createdAt, discord.TimestampStyles.LongDate)} added ${STANDING_POINT_VALUES[action.type] * Number(action.pointMultiplier)} point(s).`
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
                        .setAccentColor(STANDING_COLORS[standing.status!])
                        .addTextDisplayComponents(td => td.setContent(`# <@${user.id}>'s Account Status`))
                        .addMediaGalleryComponents(mg =>
                            mg.addItems(mgi => mgi.setURL(`https://bucket-fansbot.valbuilds.xyz/account-status/${standing.points < 15 ? standing.points : '15'}.png`))
                        )
                        .addTextDisplayComponents(td => td.setContent(`<@${user.id}>'s account is in **${STANDING_NAMES[standing.status!]}** standing, with ${standing.points} point(s).`))
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
                        .setAccentColor(ACTION_COLORS.WARN)
                        .addTextDisplayComponents(td => td.setContent([
                            `# ${ACTIONS_EMOJIS.WARN} <@${user.id}>'s Warnings`,
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
                        .setAccentColor(ACTION_COLORS.MUTE)
                        .addTextDisplayComponents(td => td.setContent([
                            `# ${ACTIONS_EMOJIS.MUTE} <@${user.id}>'s Warnings`,
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
                        .setAccentColor(ACTION_COLORS.KICK)
                        .addTextDisplayComponents(td => td.setContent([
                            `# ${ACTIONS_EMOJIS.KICK} <@${user.id}>'s Warnings`,
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
                        .setAccentColor(ACTION_COLORS.BAN)
                        .addTextDisplayComponents(td => td.setContent([
                            `# ${ACTIONS_EMOJIS.BAN} <@${user.id}>'s Warnings`,
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
    },
    {
        //@ts-ignore
        data: new discord.SlashCommandBuilder()
            .setName("account-status")
            .setDescription("account status commands")
            .addSubcommand(sc =>
                sc.setName("look-up")
                    .setDescription("Look up a user's account status.")
                    .addUserOption(opt =>
                        opt.setName("user")
                            .setDescription("The user to look up.")
                            .setRequired(true)
                    )
            )
            .addSubcommand(sc =>
                sc.setName("list")
                    .setDescription("List all users with a specific status.")
                    .addStringOption(opt =>
                        opt.setName("status")
                            .setDescription("The status to look up.")
                            .setChoices(
                                { name: "Fair", value: "fair" },
                                { name: "Bad", value: "bad" },
                                { name: "Very Bad", value: "verybad" },
                                { name: "Dangerous", value: "dangerous" },
                            )
                            .setRequired(true)
                    )
                    .addBooleanOption(opt =>
                        opt.setName("and-up")
                            .setDescription("Whether or not to see users with higher statuses. Defaults to False.")
                            .setRequired(false)
                    )
            )
            .addSubcommand(sc =>
                sc.setName("explaination")
                    .setDescription("Explains what account status is and how to understand it.")
            ),
        async execute(interaction) { }
    }
];

const textCommands: TextCommandData[] = [
    {
        name: "purge",
        async execute(message) {
            if (message.author.bot || !message.inGuild() || !message.member) return;

            const perms = discord.PermissionFlagsBits.ManageMessages;

            if (!message.member.permissionsIn(message.channel).has(perms)) {
                await message.reply("You don't have the permissions to run this command here.");
                return;
            }

            if (!message.guild.members.me?.permissionsIn(message.channel).has(perms)) {
                await message.reply("I don't have permission to manage messages in this channel.");
                return;
            }

            const arg = message.content.split(" ")[1];
            const amount = Number(arg);

            if (!arg || !Number.isInteger(amount) || amount < 1 || amount > 100) {
                await message.reply("Please provide a valid number between 1 and 100. Example: `~purge 15`.");
                return;
            }

            await message.delete().catch(() => { });
            const deleted = await message.channel.bulkDelete(amount, true);

            const notice = await message.channel.send(`Successfully deleted ${deleted.size} message(s).`);
            setTimeout(() => notice.delete().catch(() => { }), 5000);
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