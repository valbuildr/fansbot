import Client from "@/utils/Client";
import { Events } from "discord.js";
import ext from "@/ext";

const client = new Client();

client.once(Events.ClientReady, async (readyClient) => {
    console.log(`Logged in as ${readyClient.user.username}`);

    Object.entries(ext).forEach(async ([k, e]) => {
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

        if (e.contextMenus) {
            e.contextMenus.forEach((cmd) => {
                client.addContextMenu(cmd);
            });
        }

        if (e.setup) {
            await e.setup(readyClient as Client<true>);
        }
        console.log(`Loaded ${k} extension. Added ${e.slashCommands?.length ?? 0} slash commands and ${e.textCommands?.length ?? 0} text commands.`);
    });
});

client.login(process.env.DISCORD_TOKEN!);