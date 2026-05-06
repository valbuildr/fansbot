import { REST, Routes } from "discord.js";
import * as ext from "@/ext";

let commands: any[] = []
Object.values(ext).forEach((e) => {
    if (e.slashCommands) {
        e.slashCommands.forEach((cmd) => commands.push(cmd.data.toJSON()));
    }
});

const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN!);

try {
    console.log('Started refreshing application (/) commands.');

    await rest.put(Routes.applicationCommands(process.env.CLIENT_ID!), { body: commands });

    console.log('Successfully reloaded application (/) commands.');
} catch (error) {
    console.error(error);
}