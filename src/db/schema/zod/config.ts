import * as z from "zod";

export const ConfigKeys = {
    BUCKET: "bucket",
    GUILD: "guild",
    ROLES: "roles",
    CHANNELS: "channels",
    CATEGORIES: "categories"
} as const;

export type ConfigKey = (typeof ConfigKeys)[keyof typeof ConfigKeys];

export function validateConfigValue(
    key: ConfigKey,
    value: unknown
): { success: true; data: unknown; } | { success: false; error: z.ZodError } {
    const schema = getSchemaForKey(key);

    return schema.safeParse(value);
}

const schemaMap = {
    [ConfigKeys.BUCKET]: z.object({
        baseUrl: z.string(),
    }),
    [ConfigKeys.GUILD]: z.object({
        id: z.string(),
    }),
    [ConfigKeys.ROLES]: z.object({
        mod: z.string(),
        helper: z.string(),
        member: z.string(),
        unverified: z.string(),
    }),
    [ConfigKeys.CHANNELS]: z.object({
        specials: z.string(),
    }),
    [ConfigKeys.CATEGORIES]: z.object({
        other: z.string(),
        main: z.string(),
        tickets: z.string(),
    })
} satisfies Record<string, z.ZodTypeAny>;

type SchemaMap = typeof schemaMap;

export function getSchemaForKey<K extends keyof SchemaMap>(key: K): SchemaMap[K] {
    return schemaMap[key];
}