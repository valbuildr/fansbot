import db from "@/db";
import { getSchemaForKey, ConfigKeys } from "@/db/schema/zod/config";
import type { GuildMember } from "discord.js";
import type z from "zod";

const roleSchema = getSchemaForKey(ConfigKeys.ROLES);
type Config = z.infer<typeof roleSchema>;

async function configCheck(config?: Config) {
    let conf = config;
    if (!config) {
        const q = await db.query.config.findFirst({ where: (config, { eq }) => eq(config.key, "roles") });

        if (q) {
            conf = { ...q.value as any }
        } else {
            return;
        }
    }

    return conf!;
}

export async function isMod(member: GuildMember, config?: Config) {
    const conf = await configCheck(config);

    if (!conf) {
        return false;
    }

    return member.roles.cache.has(conf.mod);
}
export async function isHelper(member: GuildMember, config?: Config) {
    const conf = await configCheck(config);

    if (!conf) {
        return false;
    }

    return member.roles.cache.has(conf.helper);
}
export async function isStaff(member: GuildMember, config?: Config) {
    const conf = await configCheck(config);
    return await isMod(member, conf) || await isHelper(member, conf);
}