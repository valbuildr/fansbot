import { SlashCommandBuilder, ChatInputCommandInteraction, Message } from "discord.js"

export type SlashCommandData = {
    data: SlashCommandBuilder;
    execute: (interaction: ChatInputCommandInteraction) => Promise<any>;
};

export type TextCommandData = {
    data: {
        trigger: string;
    };
    execute: (message: Message) => Promise<any>;
};