import { GuildMemberRoleManager } from "discord.js";
import { getConfig } from "./config";
import { ConfigKeys } from "@/db/schema/zod/config";
import { getSchemaForKey } from "@/db/schema/zod/config";
import * as z from "zod";

const roleSchema = getSchemaForKey(ConfigKeys.ROLES)
type Config = z.infer<typeof roleSchema> | null;

async function configCheck(config: Config): Promise<Config> {
    return config ?? await getConfig<Config>(ConfigKeys.ROLES);
}

export async function isMod(roles: GuildMemberRoleManager | string[]) {
    const config = await getConfig<Config>(ConfigKeys.ROLES);
    if (!config) return false;

    const roleId = config.mod ?? "";

    if (Array.isArray(roles)) {
        return roles.includes(roleId);
    }

    return roles.cache.has(roleId);
}
export async function isHelper(roles: GuildMemberRoleManager | string[]) {
    const config = await getConfig<Config>(ConfigKeys.ROLES);
    if (!config) return false;

    const roleId = config.helper ?? "";

    if (Array.isArray(roles)) {
        return roles.includes(roleId);
    }

    return roles.cache.has(roleId);
}
export function isOwner(userId: string) {
    return process.env.OWNER_ID === userId;
}
export async function isStaff(roles: GuildMemberRoleManager | string[]) {
    return await isMod(roles) || await isHelper(roles);
}