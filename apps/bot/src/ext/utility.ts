import type { SlashCommandData } from "../ext";
import { MessageFlags, SlashCommandBuilder } from "discord.js";
import snowflake from "@fansbot/snowflake";

export const slashCommands: SlashCommandData[] = [
    {
        // @ts-ignore
        data: new SlashCommandBuilder()
            .setName("snowflake")
            .setDescription("Generates a snowflake using Fans Bot's generator."),
        async execute(interaction) {
            await interaction.reply({ content: `${snowflake.nextId().toString()}`, flags: MessageFlags.Ephemeral });
        },
    }
]