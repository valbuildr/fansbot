import * as p from "drizzle-orm/pg-core";
import snowflake from "@/utils/snowflake";
import type { MessageEmbed, MessageComponentRow, MessageData } from "./zod/template";

export const template = p.pgTable(
    "template",
    {
        id: p.text("id").primaryKey().$defaultFn(() => snowflake.nextId().toString()),
        name: p.text("name").notNull(),
        data: p.json("data").$type<MessageData>().notNull(),
        allowedMentions: p.text("allowed_mentions").array().notNull().default([]),

        created: p.timestamp("created", { mode: "date" }).defaultNow().notNull(),
        updated: p.timestamp("updated", { mode: "date" }).defaultNow().notNull().$onUpdate(() => new Date),
    }
).enableRLS();