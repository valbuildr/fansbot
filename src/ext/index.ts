import Client from "@/utils/Client";
import type { SlashCommandBuilder, ChatInputCommandInteraction, Message, ContextMenuCommandBuilder, ContextMenuCommandInteraction } from "discord.js";

export type SlashCommandData = {
    data: SlashCommandBuilder;
    execute: (interaction: ChatInputCommandInteraction) => Promise<any>;
};

export type TextCommandData = {
    data: {
        trigger: string;
    };
    execute: (message: Message) => Promise<any>;
};

export type ContextMenuData = {
    data: ContextMenuCommandBuilder;
    execute: (interaction: ContextMenuCommandInteraction) => Promise<any>;
}

export type ExtFile = {
    slashCommands?: SlashCommandData[];
    textCommands?: TextCommandData[];
    contextMenus?: ContextMenuData[];
    setup?: (client: Client<true>) => Promise<any>;
}

import * as status from "./status";
import * as specials from "./specials";
import * as schedules from "./schedules";
import * as memberAnnouncements from "./memberAnnouncements";
import * as templates from "./templates";

const extFiles: Record<string, ExtFile> = {
    status,
    specials,
    schedules,
    memberAnnouncements,
    templates,
};

export default extFiles;