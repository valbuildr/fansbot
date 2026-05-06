import * as p from "drizzle-orm/pg-core";

// configuration keys and schemas are in @/db/schema/zod/config.ts

export const config = p.pgTable(
    "config",
    {
        key: p.text("key").primaryKey(),
        value: p.jsonb("value").default(null),

        created: p.timestamp("created", { mode: "date" }).defaultNow().notNull(),
        updated: p.timestamp("updated", { mode: "date" }).defaultNow().notNull().$onUpdate(() => new Date),
    }
).enableRLS();