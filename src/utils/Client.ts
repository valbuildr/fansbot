import * as discord from "discord.js";
import { drizzle } from 'drizzle-orm/neon-http';

export interface SlashCommandData {
    data: discord.SlashCommandBuilder;
    execute: (interaction: discord.ChatInputCommandInteraction) => Promise<void>;
}

export interface TextCommandData {
    name: string;
    execute: (message: discord.Message) => Promise<void>;
}

export interface ConstantButtonData {
    name: string;
    data: discord.ButtonBuilder;
    execute: (interaction: discord.ButtonBuilder) => Promise<void>;
}

export default class Client<Ready extends boolean = boolean> extends discord.Client<Ready> {
    public slashCommands = new discord.Collection<string, SlashCommandData>();
    public textCommands = new discord.Collection<string, TextCommandData>();
    public constantButtons = new discord.Collection<string, ConstantButtonData>();
    public db = drizzle(process.env.DATABASE_URL!);

    public addSlashCommand(data: SlashCommandData) {
        this.slashCommands.set(data.data.name, data);
        return;
    }
    public addTextCommand(data: TextCommandData) {
        this.textCommands.set(data.name, data);
        return;
    }
    public addConstantButton(data: ConstantButtonData) {
        this.constantButtons.set(data.name, data);
        return;
    }

    public async getEmoji(name: string) {
        if (!this.application) return;
        try {
            const appEmojis = await this.application.emojis.fetch();

            const targetEmoji = appEmojis.find(emoji => emoji.name === name);

            if (targetEmoji) {
                return targetEmoji;
            } else {
                console.log(`Could not find an application emoji named: ${name}`);
            }
        } catch (error) {
            console.error('Failed to fetch application emojis:', error);
        }
    }

    constructor() {
        super({
            intents: [
                discord.GatewayIntentBits.Guilds,
                discord.GatewayIntentBits.GuildMembers,
                discord.GatewayIntentBits.GuildModeration,
                discord.GatewayIntentBits.GuildExpressions,
                discord.GatewayIntentBits.GuildIntegrations,
                discord.GatewayIntentBits.GuildWebhooks,
                discord.GatewayIntentBits.GuildInvites,
                discord.GatewayIntentBits.GuildVoiceStates,
                discord.GatewayIntentBits.GuildPresences,
                discord.GatewayIntentBits.GuildMessages,
                discord.GatewayIntentBits.GuildMessageReactions,
                discord.GatewayIntentBits.GuildMessageTyping,
                discord.GatewayIntentBits.DirectMessages,
                discord.GatewayIntentBits.DirectMessageReactions,
                discord.GatewayIntentBits.DirectMessageTyping,
                discord.GatewayIntentBits.MessageContent,
                discord.GatewayIntentBits.GuildScheduledEvents,
                discord.GatewayIntentBits.AutoModerationConfiguration,
                discord.GatewayIntentBits.AutoModerationExecution,
                discord.GatewayIntentBits.GuildMessagePolls,
                discord.GatewayIntentBits.DirectMessagePolls,
            ],
            allowedMentions: {
                repliedUser: false
            }
        })
    }
}