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
    if (message.author.bot || !message.inGuild() || !message.member) return;

    if (message.content.startsWith("~purge")) {
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
    } else if (message.content.startsWith("~sync")) {
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