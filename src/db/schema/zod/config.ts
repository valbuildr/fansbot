import * as z from "zod";

export const ConfigKeys = {
    ROLES: "roles",
    CHANNELS: "channels"
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
    [ConfigKeys.ROLES]: z.object({
        mod: z.string(),
        helper: z.string(),
    }),
    [ConfigKeys.CHANNELS]: z.object({
        specials: z.string(),
    })
} satisfies Record<string, z.ZodTypeAny>;

type SchemaMap = typeof schemaMap;

export function getSchemaForKey<K extends keyof SchemaMap>(key: K): SchemaMap[K] {
    return schemaMap[key];
}