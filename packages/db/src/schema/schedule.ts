import snowflake from "@fansbot/snowflake";
import * as p from "drizzle-orm/pg-core";

export const channelType = p.pgEnum("channel_type", [
    "tv",
    "radio",
    "regionalRadio",
    "other"
]);

export const channel = p.pgTable(
    "channel",
    {
        sid: p.text("sid").primaryKey(),
        nid: p.text("nid").notNull(),
        channelName: p.text("channel_name").notNull(),
        channelRegion: p.text("channel_region"),
        type: channelType("type").notNull(),
        bbcId: p.text("bbc_id").notNull().unique(),
        banner: p.text("banner").notNull(),
        color: p.text("color"),
    }
).enableRLS();

export const autoSchedules = p.pgTable(
    "auto_schedules",
    {
        id: p.text("id").primaryKey().$defaultFn(() => snowflake.nextId().toString()),
        sid: p.text("sid").notNull().references(() => channel.sid, { onDelete: "cascade" }),
        postTo: p.text("post_to").notNull(),
        order: p.integer("order").notNull(),
        messageId: p.text("message_id"),
        cache: p.jsonb("cache"),
    }
).enableRLS();