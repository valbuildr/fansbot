import { REST, Routes } from "discord.js";
import ext from "./ext";
import db from "@fansbot/db";
import * as schema from "@fansbot/db/schema";
import { eq } from "drizzle-orm";

let commands: any[] = []
Object.values(ext).forEach((e) => {
    if (e.slashCommands) {
        e.slashCommands.forEach((cmd) => commands.push(cmd.data.toJSON()));
    }
});

const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN!);

try {
    console.log(`Started refreshing ${commands.length} application (/) commands.`);

    const resp = await rest.put(Routes.applicationCommands(process.env.DISCORD_CLIENT_ID!), { body: commands }) as any[];

    for (const item of resp) {
        const q = await db.query.command.findFirst({ where: eq(schema.command.name, item.name) });

        if (q) {
            await db.update(schema.command).set({ name: item.name, id: item.id, data: item }).where(eq(schema.command.name, item.name));
        } else {
            await db.insert(schema.command).values({ name: item.name, id: item.id, data: item });
        }
    }

    console.log(`Successfully reloaded ${commands.length} application (/) commands.`);
} catch (error) {
    console.error(error);
}
