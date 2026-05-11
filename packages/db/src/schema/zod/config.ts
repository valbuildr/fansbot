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

export const bucketSchema = z.object({
    baseUrl: z.string(),
});
export const guildSchema = z.object({
    id: z.string(),
});
export const rolesSchema = z.object({
    mod: z.string(),
    helper: z.string(),
    member: z.string(),
    unverified: z.string(),
});
export const channelsSchema = z.object({
    specials: z.string(),
    newMembers: z.string(),
    rules: z.string(),
});
export const categoriesSchema = z.object({
    other: z.string(),
    main: z.string(),
    tickets: z.string(),
});

export type Bucket = z.infer<typeof bucketSchema>;
export type Guild = z.infer<typeof guildSchema>;
export type Roles = z.infer<typeof rolesSchema>;
export type Channels = z.infer<typeof channelsSchema>;
export type Categories = z.infer<typeof categoriesSchema>;

const schemaMap = {
    [ConfigKeys.BUCKET]: bucketSchema,
    [ConfigKeys.GUILD]: guildSchema,
    [ConfigKeys.ROLES]: rolesSchema,
    [ConfigKeys.CHANNELS]: channelsSchema,
    [ConfigKeys.CATEGORIES]: categoriesSchema
} satisfies Record<string, z.ZodTypeAny>;

type SchemaMap = typeof schemaMap;

export function getSchemaForKey<K extends keyof SchemaMap>(key: K): SchemaMap[K] {
    return schemaMap[key];
}