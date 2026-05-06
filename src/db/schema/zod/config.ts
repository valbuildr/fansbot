import * as z from "zod";

export const ConfigKeys = {
    ROLES: "roles"
} as const;

export type ConfigKey = (typeof ConfigKeys)[keyof typeof ConfigKeys];

const schemaMap = {
    [ConfigKeys.ROLES]: z.object({
        mod: z.string(),
        helper: z.string(),
    }),
} satisfies Record<string, z.ZodTypeAny>;

type SchemaMap = typeof schemaMap;

export function getSchemaForKey<K extends keyof SchemaMap>(key: K): SchemaMap[K] {
    return schemaMap[key];
}