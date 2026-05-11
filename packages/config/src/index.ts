import db from "@fansbot/db";
import { validateConfigValue, type ConfigKey } from "@fansbot/db/schema/zod";
import { eq } from "drizzle-orm";
import * as schema from "@fansbot/db/schema";

export async function getConfig<T = unknown>(
    key: ConfigKey
): Promise<T | null> {
    const config = await db.query.config.findFirst({
        where: eq(schema.config.key, key),
    });

    if (!config) return null;

    const raw = getStoredConfigValue(config, key);

    return (raw?.value as T) ?? null;
}

export async function getFullConfig(): Promise<Record<ConfigKey, unknown>> {
    const configs = await db.query.config.findMany();

    const result: Record<string, unknown> = {};

    for (const config of configs) {
        const raw = getStoredConfigValue(config, config.key as ConfigKey);

        result[config.key] = raw?.value ?? null;
    }

    return result as Record<ConfigKey, unknown>;
}

export async function setConfig(
    key: ConfigKey,
    value: unknown
): Promise<void> {
    const validation = validateConfigValue(key, value);

    if (!validation.success) {
        throw new Error(`Invalid config value for ${key}: ${validation.error.message}`);
    }

    const normalizedValue = validation.data;

    const existing = await db.query.config.findFirst({
        where: eq(schema.config.key, key),
    });

    if (existing) {
        await db
            .update(schema.config)
            .set({
                value: normalizedValue
            })
            .where(eq(schema.config.key, key));
    } else {
        await db.insert(schema.config).values({
            key,
            value: normalizedValue
        });
    }
}

export async function deleteConfig(key: ConfigKey): Promise<void> {
    await db.delete(schema.config).where(eq(schema.config.key, key));
}

function getStoredConfigValue(
    config: typeof schema.config.$inferSelect,
    key: ConfigKey
): { value: unknown } | null {
    return {
        value: config.value
    }
}