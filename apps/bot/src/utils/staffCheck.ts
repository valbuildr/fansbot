import { GuildMemberRoleManager } from "discord.js";
import { getConfig } from "@fansbot/config";
import * as zodSchema from "@fansbot/db/schema/zod";

export async function isMod(roles: GuildMemberRoleManager | string[]) {
    const config = await getConfig<zodSchema.Roles>(zodSchema.ConfigKeys.ROLES);
    if (!config) return false;

    const roleId = config.mod ?? "";

    if (Array.isArray(roles)) {
        return roles.includes(roleId);
    }

    return roles.cache.has(roleId);
}
export async function isHelper(roles: GuildMemberRoleManager | string[]) {
    const config = await getConfig<zodSchema.Roles>(zodSchema.ConfigKeys.ROLES);
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