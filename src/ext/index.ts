import Client from "@/utils/Client";
import type { SlashCommandData, TextCommandData } from "@/utils/commandTypes";

export type ExtFile = {
    slashCommands?: SlashCommandData[];
    textCommands?: TextCommandData[];
    setup?: (client: Client<true>) => Promise<any>;
}

import * as status from "./status";
import * as specials from "./specials";
import * as schedules from "./schedules";
import * as memberAnnouncements from "./memberAnnouncements";
import * as template from "./templates";

const extFiles: Record<string, ExtFile> = {
    status,
    specials,
    schedules,
    memberAnnouncements,
    template,
};

export default extFiles;