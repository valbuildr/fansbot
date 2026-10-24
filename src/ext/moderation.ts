import * as discord from "discord.js";
import Client from "../utils/Client";
import { type SlashCommandData } from "../utils/Client";
import { modAction } from "../db/schema";
import { eq } from "drizzle-orm";

const profileCommand: SlashCommandData = {
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

        const actionEmojis = {
            "WARN": "⚠️",
            "MUTE": "🔇",
            "KICK": "👢",
            "BAN": "🔨",
        };

        const container = new discord.ContainerBuilder()
            .setAccentColor(discord.Colors.Blurple)
            .addSectionComponents(s =>
                s.addTextDisplayComponents(td =>
                    td.setContent([
                        `# ${user.username}'s Moderation Profile`,
                        `${actionEmojis.WARN} **${activeWarnings.length} active warning(s)** (${expiredWarnings.length} expired)`,
                        `${actionEmojis.MUTE} **${activeMutes.length} active mutes(s)** (${expiredMutes.length} expired)`,
                        `${actionEmojis.KICK} **${activeKicks.length} active kick(s)** (${expiredKicks.length} expired)`,
                        `${actionEmojis.BAN} **${activeBans.length} active bans(s)** (${expiredBans.length} expired)`,
                    ].join("\n"))
                )
                    .setThumbnailAccessory(tb =>
                        tb.setURL(user.displayAvatarURL())
                    )
            );

        const actionNames = {
            "WARN": "Warning",
            "MUTE": "Mute",
            "KICK": "Kick",
            "BAN": "Ban",
        };

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
                            .setCustomId(`modaction-${mostRecent.id}`)
                            .setLabel("More Details")
                            .setEmoji(actionEmojis[mostRecent.type])
                            .setStyle(discord.ButtonStyle.Secondary)
                    )
            )
        }

        // determine account standing
        let standingScore = 0;

        // warning    1pt
        standingScore += activeWarnings.length;
        // mute       3pts
        standingScore += activeMutes.length * 3;
        // kick       5pts
        standingScore += activeKicks.length * 5;
        // ban        10pts
        standingScore += activeBans.length * 10;

        // fair       0-4 pts
        // bad        5-9 pts
        // very bad   10-14 pts
        // dangerous  15+ pts

        let standingEmoji = "";
        let standing = "";

        if (standingScore < 5) {
            standingEmoji = "🟢";
            standing = "Fair";
        } else if (standingScore > 4 && standingScore < 10) {
            standingEmoji = "🟡";
            standing = "Bad";
        } else if (standingScore > 9 && standingScore < 15) {
            standingEmoji = "🟠";
            standing = "Very Bad";
        } else if (standingScore > 15) {
            standingEmoji = "🔴";
            standing = "Dangerous";
        }

        container.addSeparatorComponents(s => s.setSpacing(discord.SeparatorSpacingSize.Large));
        container.addSectionComponents(s =>
            s.addTextDisplayComponents(td =>
                td.setContent([
                    `## Account Standing`,
                    `**${interaction.user.username}**'s account is in ${standingEmoji} **${standing}** condition.`
                ].join("\n"))
            )
                .setButtonAccessory(
                    new discord.ButtonBuilder()
                        .setCustomId(`standing-${user.id}`)
                        .setLabel("More Details")
                        .setEmoji(standingEmoji)
                        .setStyle(discord.ButtonStyle.Secondary)
                )
        );

        container.addSeparatorComponents(s => s.setSpacing(discord.SeparatorSpacingSize.Large));
        container.addActionRowComponents(
            new discord.ActionRowBuilder<discord.ButtonBuilder>()
                .addComponents(
                    new discord.ButtonBuilder()
                        .setCustomId(`warns-${user.id}`)
                        .setEmoji(actionEmojis.WARN)
                        .setLabel("See all Warnings")
                        .setDisabled(warnings.length <= 1)
                        .setStyle(discord.ButtonStyle.Secondary),
                    new discord.ButtonBuilder()
                        .setCustomId(`mutes-${user.id}`)
                        .setEmoji(actionEmojis.MUTE)
                        .setLabel("See all Mutes")
                        .setDisabled(mutes.length <= 1)
                        .setStyle(discord.ButtonStyle.Secondary),
                    new discord.ButtonBuilder()
                        .setCustomId(`kicks-${user.id}`)
                        .setEmoji(actionEmojis.KICK)
                        .setLabel("See all Kicks")
                        .setDisabled(kicks.length <= 1)
                        .setStyle(discord.ButtonStyle.Secondary),
                    new discord.ButtonBuilder()
                        .setCustomId(`bans-${user.id}`)
                        .setEmoji(actionEmojis.BAN)
                        .setLabel("See all Bans")
                        .setDisabled(bans.length <= 1)
                        .setStyle(discord.ButtonStyle.Secondary),
                )
        )

        await interaction.reply({
            components: [container],
            flags: respondEph
                ? [discord.MessageFlags.IsComponentsV2, discord.MessageFlags.Ephemeral]
                : [discord.MessageFlags.IsComponentsV2],
        });
    }
}

export async function setup(client: Client<true>): Promise<void> {
    client.slashCommands.set(profileCommand.data.name, profileCommand);

    console.log("Moderation extension loaded.");
    return;
}