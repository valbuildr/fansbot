import Client from "@/utils/Client";
import { Events } from "discord.js";
import * as ext from "@/ext";
import type { SlashCommandData, TextCommandData } from "./utils/commandTypes";

const client = new Client();

client.once(Events.ClientReady, async (readyClient) => {
    console.log(`Logged in as ${readyClient.user.username}`);

    type Module = {
        slashCommands?: SlashCommandData[];
        textCommands?: TextCommandData[];
        setup?: (client: Client<true>) => Promise<void>;
    }

    Object.entries(ext as Record<string, Module>).forEach(async ([k, e]) => {
        console.log(`Loading ${k} extension...`);
        if (e.slashCommands) {
            e.slashCommands.forEach((cmd) => {
                client.addSlashCommand(cmd);
            });
        }

        if (e.textCommands) {
            e.textCommands.forEach((cmd) => {
                client.addTextCommand(cmd);
            });
        }

        if (e.setup) {
            await e.setup(readyClient as Client<true>);
        }
        console.log(`Loaded ${k} extension. Added ${e.slashCommands?.length ?? 0} slash commands and ${e.textCommands?.length ?? 0} text commands.`);
    });
});

client.login(process.env.DISCORD_TOKEN!);