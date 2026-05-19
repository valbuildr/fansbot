import * as p from "drizzle-orm/pg-core";

export const command = p.pgTable(
    "command",
    {
        name: p.text("name").primaryKey(),
        id: p.text("id").notNull().unique(),
        data: p.json("data").notNull(),
    }
).enableRLS();