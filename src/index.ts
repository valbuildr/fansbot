import * as discord from "discord.js";
import Client from "./utils/Client";

import { setup as schedulesSetup } from "./ext/schedules";
import { setup as moderationSetup } from "./ext/moderation";

const client = new Client();

client.once(discord.Events.ClientReady, async (rCLient) => {
    console.log(`Logged in as ${rCLient.user.displayName}`);

    const c = rCLient as Client<true>;

    await schedulesSetup(c);
    await moderationSetup(c);

    c.user.setActivity({
        name: "hellow there!",
        type: discord.ActivityType.Custom,
        state: `Keeping up with the BBC`
    });
});

client.on(discord.Events.MessageCreate, async (message) => {
    if (message.content.startsWith("~sync")) {
        if (message.author.bot || !message.inGuild() || !message.member) return;

        if (!message.member.permissionsIn(message.channel).has(discord.PermissionFlagsBits.Administrator)) {
            await message.reply("You don't have the permissions to run this command here.");
            return;
        }

        const rest = new discord.REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN!);

        const commands = client.slashCommands.map((s) => s.data.toJSON())

        const reply = await message.reply({ content: `Started refreshing ${commands.length} application command(s)...` });
        try {
            console.log(`Started refreshing ${commands.length} application command(s)...`);

            await rest.put(discord.Routes.applicationCommands(process.env.DISCORD_CLIENT_ID!), { body: commands });

            await reply.edit({ content: `Successfully reloaded ${commands.length} application command(s).` });
            console.log(`Successfully reloaded ${commands.length} application command(s).`);
        } catch (error) {
            await reply.edit({ content: "An error ocurred." })
            console.error(error);
        }
    } else if (message.content.startsWith("~")) {
        const name = message.content.slice(1).split(" ")[0];
        const cmd = client.textCommands.find(c => c.name === name);

        if (cmd) {
            await cmd.execute(message);
        }
    }
});

client.on(discord.Events.InteractionCreate, async (interaction) => {
    const client = interaction.client as Client;
    if (interaction.isChatInputCommand()) {
        const command = client.slashCommands.find(cmd => cmd.data.name === interaction.commandName);

        if (!command) {
            await interaction.reply({ content: "This command does not exist.", flags: discord.MessageFlags.Ephemeral });
            return;
        }

        await command.execute(interaction);
    }
})

client.login(process.env.DISCORD_TOKEN!);