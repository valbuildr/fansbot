import * as p from "drizzle-orm/pg-core";
import snowflake from "@/utils/snowflake";

export const statusType = p.pgEnum(
    "status_type",
    [
        "competing",
        "listening",
        "playing",
        "streaming",
        "watching",
    ]
);

export const status = p.pgTable(
    "status",
    {
        id: p.text("id").primaryKey().$defaultFn(() => snowflake.nextId().toString()),
        name: p.text("name").notNull(),
        type: statusType().notNull().default("playing"),

        created: p.timestamp("created", { mode: "date" }).defaultNow().notNull(),
        updated: p.timestamp("updated", { mode: "date" }).defaultNow().notNull().$onUpdate(() => new Date),
    }
);