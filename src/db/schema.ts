import * as p from "drizzle-orm/pg-core";

export const modActionType = p.pgEnum("mod_action_type", [
    "WARN",
    "MUTE",
    "KICK",
    "BAN"
]);

export const modAction = p.pgTable("mod_action", {
    id: p.integer("id").primaryKey().generatedAlwaysAsIdentity(),
    type: modActionType("type").notNull(),
    user: p.text("user").notNull(),
    author: p.text("author").notNull(),
    reason: p.text("reason").notNull(),
    proof: p.text("proof").array(),
    createdAt: p.timestamp("created_at", { precision: 6, withTimezone: true }).notNull().defaultNow(),
    isActive: p.boolean("is_active").notNull().default(true),
    expiresAt: p.timestamp("expires_at", { precision: 6, withTimezone: true }),
});