import { Client as DClient, GatewayIntentBits, Collection, Events, MessageFlags } from "discord.js";
import type { SlashCommandData, TextCommandData, ContextMenuData } from "../ext";
import db from "@fansbot/db";

export default class Client<Ready extends boolean = boolean> extends DClient<Ready> {
    public database = db;
    public slashCommands = new Collection<string, SlashCommandData>();
    public textCommands = new Collection<string, TextCommandData>();
    public contextMenus = new Collection<string, ContextMenuData>();

    public addSlashCommand(data: SlashCommandData) {
        this.slashCommands.set(data.data.name, data);
    }
    public addTextCommand(data: TextCommandData) {
        this.textCommands.set(data.data.trigger, data);
    }
    public addContextMenu(data: ContextMenuData) {
        this.contextMenus.set(data.data.name, data);
    }

    constructor() {
        super({
            intents: Object.values(GatewayIntentBits).filter((v): v is GatewayIntentBits => typeof v === "number")
        });

        this.on(Events.InteractionCreate, async (interaction) => {
            if (interaction.isChatInputCommand()) {
                const cmd = this.slashCommands.get(interaction.commandName);

                if (!cmd) {
                    console.error(`No command matching ${interaction.commandName} was found.`);
                    return;
                }

                try {
                    await cmd.execute(interaction);
                } catch (error) {
                    console.error(error);
                    if (interaction.replied || interaction.deferred) {
                        await interaction.followUp({
                            content: 'There was an error while executing this command!',
                            flags: MessageFlags.Ephemeral,
                        });
                    } else {
                        await interaction.reply({
                            content: 'There was an error while executing this command!',
                            flags: MessageFlags.Ephemeral,
                        });
                    }
                }
            } else if (interaction.isContextMenuCommand()) {
                const cmd = this.contextMenus.get(interaction.commandName);

                if (!cmd) {
                    console.error(`No command matching ${interaction.commandName} was found.`);
                    return;
                }

                try {
                    await cmd.execute(interaction);
                } catch (error) {
                    console.error(error);
                    if (interaction.replied || interaction.deferred) {
                        await interaction.followUp({
                            content: 'There was an error while executing this command!',
                            flags: MessageFlags.Ephemeral,
                        });
                    } else {
                        await interaction.reply({
                            content: 'There was an error while executing this command!',
                            flags: MessageFlags.Ephemeral,
                        });
                    }
                }
            }

            return;
        });

        this.on(Events.MessageCreate, async (message) => {
            if (message.content.startsWith("$")) {
                const cmd = this.textCommands.get(message.content.slice(1, message.content.length).split(" ")[0] ?? "");

                if (cmd) {
                    try {
                        await cmd.execute(message);
                    } catch (error) {
                        console.error(error);

                        await message.channel.send({ content: 'There was an error while executing this command!', })
                    }
                }
            }
        })
    }
}