import * as discord from "discord.js"
import Client from "../utils/Client";
import { readFromStorage, writeToStorage } from "../utils/simpleDataStorage";

// helper: accepts any string but keeps autocomplete for known literals
type LooseString<T extends string> = T | (string & {});

interface IblResponse {
    schema: string;
    version: string;
    status?: { service: string; release: string };
    error?: { details: string; http_response_code: number };
    categories?: Category[];
    channels?: Channel[];
    regions?: Region[];
    region?: Region;
    episodes?: Episode[];
    programmes?: Programme[];
    programme_episodes?: ProgrammeEpisodes;
    programme_watching?: ProgrammeWatching;
    group_episodes?: GroupEpisodes;
    episode_recommendations?: EpisodeRecommendations;
    broadcasts?: Broadcasts;
    schedule?: Schedule;
    category_programmes?: CategoryProgrammes;
    channel_programmes?: ChannelProgrammes;
    atoz_programmes?: AtozProgrammes;
    channel_highlights?: ChannelHighlights;
    category_highlights?: CategoryHighlights;
    prerolls?: Trailer[];
    new_search?: NewSearch;
    watching?: WatchingList;
    user_recommendations?: UserRecommendations;
    added?: AddedList;
    adds?: Adds;
    next?: Next;
    category?: Category;
    clips?: Clip[];
}

interface Paged {
    page: number;
    per_page: number;
    count: number;
}

interface ProgrammeEpisodes extends Paged {
    elements: Episode[];
    programme: Programme;
}

interface ProgrammeWatching extends Paged {
    elements: Array<Episode | Watching>;
}

interface GroupEpisodes extends Paged {
    elements: Episode[];
    group?: Group;
}

interface EpisodeRecommendations {
    count: number;
    elements: Episode[];
    blend: "curated" | "algorithmic";
}

interface Broadcasts extends Paged {
    elements: Broadcast[];
    channel: Channel;
}

interface Schedule {
    elements: Broadcast[];
    channel: Channel;
}

interface CategoryProgrammes extends Paged {
    category: Category;
    elements: Programme[];
}

interface ChannelProgrammes extends Paged {
    channel: Channel;
    elements: Programme[];
}

interface AtozProgrammes extends Paged {
    character: string;
    elements: Programme[];
}

interface ChannelHighlights {
    channel: Channel;
    elements: Array<Episode | Group | Promotion>;
}

interface CategoryHighlights {
    category: Category;
    elements: Array<Episode | Group | Promotion>;
}

interface NewSearch {
    query: string;
    results: Array<Episode | Programme>;
}

interface WatchingList {
    elements: Watching[];
    count: number;
    count_all: number;
}

interface UserRecommendations {
    elements: UserRecommendation[];
    rec_source: string;
    rec_feed?: string;
    rec_set: string;
}

interface AddedList {
    elements: Added[];
    count: number;
    count_all: number;
}

interface Adds {
    id: string;
    added: string;
}

interface Next {
    programme?: Episode[];
}

interface Category {
    id: string;
    type: "category";
    title: string;
    kind: "genre" | "accessibility" | "national" | "childrens";
    child_episode_count?: number;
    child_programme_count?: number;
    parent_category?: string;
    contextual_title?: string;
    sub_categories?: Category[];
}

interface Channel {
    id: string;
    type: "channel";
    title: string;
    has_schedule: boolean;
    master_brand_id: string;
    master_brand_title: string;
    on_air?: boolean;
}

interface Region {
    id: string;
    short_id: string;
    type: "region";
    title: string;
    kind: "regional" | "national";
}

type AgeBand = "u13" | "u16" | "u18" | "o18";

type ProgrammeType =
    | "narrative"
    | "sequential"
    | "self-contained"
    | "strand"
    | "unclassified"
    | "one-off";

interface EpisodeTest {
    id: string;
    variants: Array<{
        id: string;
        data: {
            images: {
                type?: "episode" | "episode_large";
                standard?: string;
            };
        };
    }>;
    status: "active";
}

interface EpisodeImages {
    type: "image";
    standard: string;
    live?: string;
    character_image?: string;
    inherited_from?: string;
    promotional?: string;
    promotional_with_logo?: string;
    portrait?: string;
    promotional_left_safe_zone?: string;
}

interface EpisodeSynopses {
    small?: string;
    medium?: string;
    large?: string;
    editorial?: string;
    preview?: string;
    programme_small?: string;
    live?: string;
}

interface EpisodeLabels {
    editorial?: string;
    time?: string;
    category?: string;
    editorial_category?: string;
}

interface RelatedLink {
    id: string;
    url: string;
    kind: string;
    title: string;
    type: "link";
}

interface Episode {
    id: string;
    type: "episode" | "episode_large";
    title: string;
    tests?: EpisodeTest[];
    original_title?: string;
    live?: boolean;
    images: EpisodeImages;
    has_credits?: boolean;
    signed: boolean;
    childrens?: boolean;
    audio_described: boolean;
    status: "available" | "unavailable";
    requires_tv_licence?: boolean;
    requires_sign_in: boolean;
    tleo_id: string;
    guidance: boolean;
    subtitle?: string;
    editorial_subtitle?: string;
    editorial_title?: string;
    live_title?: string;
    live_subtitle?: string;
    slice_subtitle?: string;
    event_group_id?: string;
    preview_id?: string;
    preview_clip_id?: string;
    slice_id?: string;
    synopses: EpisodeSynopses;
    versions: Version[];
    parent_id?: string;
    tleo_type: "episode" | "brand" | "series";
    programme_type?: ProgrammeType;
    categories: string[];
    labels?: EpisodeLabels;
    master_brand: MasterBrand;
    parent_position?: number;
    release_date_time?: string;
    lexical_sort_letter: string;
    numeric_tleo_position?: number | null;
    release_date?: string;
    related_links?: RelatedLink[];
    promoted?: boolean;
    /** minItems: 1, uniqueItems: true */
    requires_ab?: [AgeBand, ...AgeBand[]];
}

interface Programme {
    id: string;
    type: "programme" | "programme_large";
    title: string;
    labels?: { category?: string; editorial_info?: string };
    tleo_type?: "brand" | "series" | "episode";
    synopses: { small?: string; medium?: string; large?: string };
    lexical_sort_letter: string;
    images: {
        type: "image";
        standard: string;
        inherited_from?: string;
        promotional?: string;
        logo?: string;
        promotional_with_logo?: string;
        promotional_left_safe_zone?: string;
    };
    master_brand: MasterBrand;
    categories: string[];
    status: "available" | "unavailable" | "coming_soon";
    count: number;
    programme_type?: ProgrammeType;
    live: boolean;
    initial_children: Episode[];
}

interface MasterBrand {
    id: string;
    titles: { small: string; medium: string; large: string };
    attribution: string;
}

interface Group {
    content_type: "episodes" | "programmes";
    id: string;
    type: "group" | "group_large";
    title: string;
    short_title?: string;
    group_type: "curated" | "automated";
    stacked?: boolean;
    images?: {
        type: "image";
        standard: string;
        vertical: string;
        promotional?: string;
        banner?: string;
    };
    episode_sort_direction?: string;
    synopses?: { small?: string; medium?: string; large?: string };
    related_links?: Array<{ kind: string; url: string; title: string }>;
    initial_children?: Array<Episode | Broadcast>;
    count?: number;
    labels?: {
        editorial?: string;
        category?: string;
    };
}

interface Broadcast {
    id: string;
    episode_id: string;
    version_id: string;
    service_id: string;
    type: "broadcast";
    scheduled_start: string;
    scheduled_end: string;
    transmission_start?: string;
    transmission_end?: string;
    duration?: { text: string; value: string };
    blanked: boolean;
    repeat: boolean;
    episode: Episode;
    channel_title?: string;
    available_on_hd_service?: string | null;
    events?: Array<{ name: string; system: string; time: string }>;
}

interface Promotion {
    id: string;
    type: "promotion";
    title?: string;
    subtitle?: string;
    url?: string;
    synopses?: { small?: string; medium?: string; large?: string };
    images?: { type: "image"; standard: string; inherited_from?: string };
    labels?: { promotion: string };
}

interface Trailer {
    id: string;
    type: "trailer";
    title: string;
    kind:
    | "available_now"
    | "watch_now"
    | "coming_soon"
    | "streaming_now_sounds"
    | "other";
    version_id: string;
    message: string;
}

interface Watching {
    urn: string;
    type: "watching";
    episode: Episode;
    programme: Programme;
    version: Version;
    status?: "current" | "next" | "ended";
    offset?: number;
    progress?: number;
    remaining?: number;
    has_next: boolean;
}

interface UserRecommendation {
    algorithm: string;
    type: "user_recommendation";
    episode: Episode;
}

interface Added {
    urn: string;
    type: "added";
    programme: Programme;
}

interface Interaction {
    title: {
        short: LooseString<"Skip">;
        long: LooseString<"Skip intro" | "Skip recap" | "Skip preview">;
    };
    type: LooseString<"skip">;
    subtype: LooseString<
        "intro" | "recap" | "this-episode-preview" | "next-episode-teaser"
    >;
    interaction_points: { show_from: number; skip_to: number };
}

type VersionKind =
    | "legal"
    | "editorial"
    | "technical-replacement"
    | "original"
    | "iplayer-version"
    | "lengthened"
    | "shortened"
    | "pre-watershed"
    | "post-watershed"
    | "warnings-higher"
    | "warnings-lower"
    | "warnings-none"
    | "duplication"
    | "open-subtitled"
    | "other"
    | "audio-described"
    | "signed"
    | "webcast"
    | "simulcast";

type VersionEvent =
    | { name: string; system: string; offset: number }
    | { name: string; system: string; time: string };

interface Version {
    id: string;
    type: "version" | "version_large";
    hd: boolean;
    uhd?: boolean;
    hdr?: boolean;
    download: boolean;
    kind: VersionKind;
    duration: { text: string; value: string };
    rrc?: {
        url?: string;
        description: { small: string; large: string };
    };
    guidance?: {
        id: string;
        text?: { small?: string; medium?: string; large?: string };
    };
    first_broadcast?: string;
    first_broadcast_date_time?: string;
    credits_start?: number;
    service_id?: string;
    regional_services?: Record<string, string>;
    availability: {
        start: string;
        accurate_start?: string;
        end?: string;
        remaining?: { text: string };
    };
    events?: VersionEvent[];
    interactions?: Interaction[];
}

interface Clip {
    id: string;
    type: "clip";
    title: string;
    subtitle?: string;
    images: { type: "image"; standard: string; inherited_from?: string };
    tleo_id: string;
    synopses: {
        small?: string;
        medium?: string;
        large?: string;
        editorial?: string;
    };
    versions: Version[];
    content_type: string;
    tleo_type?: "episode" | "brand" | "series" | "clip";
    labels?: { editorial?: string; category?: string };
    promotion_type?: "available_now" | "coming_soon";
    master_brand: MasterBrand;
    onward_journey?: { type?: "episode"; id?: string };
}

const SCHEDULE_DAY_START_HOUR = 6;

function getScheduleDate(date: Date): string {
    const shifted = new Date(date.getTime() - SCHEDULE_DAY_START_HOUR * 60 * 60 * 1000);

    return new Intl.DateTimeFormat("en-CA", {
        timeZone: "Europe/London",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
    }).format(shifted);
}

async function fetchSchedule(channel: string, date: Date): Promise<IblResponse | null> {
    const dateStr = getScheduleDate(date);

    const res = await fetch(`https://ibl.api.bbci.co.uk/ibl/v1/channels/${channel}/schedule/${dateStr}`);
    if (!res.ok) {
        console.error(`HTTP ${res.status}`);
        console.log(await res.text());
        return null;
    };

    const data = (await res.json()) as IblResponse;
    return data;
}

type ChannelConfig = {
    name: string;
    region?: string;
    image: string;
    color: number;
    scheduleLink: string;
}

export const allChannels: Record<string, ChannelConfig> = {
    bbc_one_cambridge: {
        name: "BBC One",
        region: "Cambridgeshire",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6h",
    },
    bbc_one_channel_islands: {
        name: "BBC One",
        region: "Channel Islands",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6j",
    },
    bbc_one_east: {
        name: "BBC One",
        region: "East",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6k",
    },
    bbc_one_east_midlands: {
        name: "BBC One",
        region: "East Midlands",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6l",
    },
    bbc_one_london: {
        name: "BBC One",
        region: "London",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6p",
    },
    bbc_one_north_east: {
        name: "BBC One",
        region: "North East & Cumbria",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6r",
    },
    bbc_one_north_west: {
        name: "BBC One",
        region: "North West",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6s",
    },
    bbc_one_northern_ireland: {
        name: "BBC One",
        region: "Northern Ireland",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6q",
    },
    bbc_one_oxford: {
        name: "BBC One",
        region: "Oxfordshire",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6t",
    },
    bbc_one_scotland: {
        name: "BBC One",
        region: "Scotland",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6v",
    },
    bbc_one_south: {
        name: "BBC One",
        region: "South",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6w",
    },
    bbc_one_south_east: {
        name: "BBC One",
        region: "South East",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6x",
    },
    bbc_one_south_west: {
        name: "BBC One",
        region: "South West",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6y",
    },
    bbc_one_wales: {
        name: "BBC One",
        region: "Wales",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6z",
    },
    bbc_one_west: {
        name: "BBC One",
        region: "West",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl70",
    },
    bbc_one_west_midlands: {
        name: "BBC One",
        region: "West Midlands",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl71",
    },
    bbc_one_east_yorkshire: {
        name: "BBC One",
        region: "East Yorks & Lincs",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6m",
    },
    bbc_one_yorks: {
        name: "BBC One",
        region: "Yorkshire",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/one.png",
        color: 0xEA2923,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl72",
    },

    bbc_two_england: {
        name: "BBC Two",
        region: "England",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/two.png",
        color: 0x01454E,
        scheduleLink: "https://www.bbc.co.uk/schedules/p015pksy",
    },

    bbc_four: {
        name: "BBC Four",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/four.png",
        color: 0x000000,
        scheduleLink: "https://www.bbc.co.uk/schedules/p01kv81d",
    },

    cbbc: {
        name: "CBBC",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/cbbc.png",
        color: 0x4023E0,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl9r",
    },

    cbeebies: {
        name: "Cbeebies",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/cbeebies.png",
        color: 0x1079EB,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl9r",
    },

    bbc_news24: {
        name: "BBC News",
        region: "UK",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/news.png",
        color: 0xB80000,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl6g",
    },

    bbc_parliament: {
        name: "BBC Parliament",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/parliament.png",
        color: 0xB80000,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl73",
    },

    bbc_alba: {
        name: "BBC Alba",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/alba.png",
        color: 0x003167,
        scheduleLink: "https://www.bbc.co.uk/schedules/p00fzl67",
    },

    s4cpbs: {
        name: "S4C",
        image: "https://bucket-fansbot.valbuilds.xyz/schedule-banners/tv/s4c.png",
        color: 0x008A9A,
        scheduleLink: "https://www.bbc.co.uk/schedules/p020dmkf",
    }
};

async function fmtSchedule(client: Client<true>, schedule: IblResponse, channelConfig: ChannelConfig): Promise<discord.ContainerBuilder> {
    const now = new Date();

    const container = new discord.ContainerBuilder()
        .setAccentColor(channelConfig.color)
        .addMediaGalleryComponents(mg =>
            mg.addItems(
                new discord.MediaGalleryItemBuilder()
                    .setURL(channelConfig.image)
            )
        )
        .addTextDisplayComponents(td =>
            td.setContent(channelConfig.region ? `# ${channelConfig.name} [${channelConfig.region}]` : `# ${channelConfig.name}`)
        );

    if (!schedule.schedule) {
        console.log(JSON.stringify(schedule));
        throw new Error("Schedule data is malformed");
    }

    const broadcasts = schedule.schedule.elements;

    const MAX_UPCOMING = 5;

    const startOf = (b: Broadcast) => new Date(b.scheduled_start);
    const endOf = (b: Broadcast) => new Date(b.scheduled_end);

    const current = broadcasts.filter(
        (b) => startOf(b).getTime() <= now.getTime() && now.getTime() < endOf(b).getTime(),
    );

    const upcoming = broadcasts
        .filter((b) => startOf(b).getTime() > now.getTime())
        .sort((a, b) => startOf(a).getTime() - startOf(b).getTime())
        .slice(0, MAX_UPCOMING);

    const liveEmoji = await client.getEmoji("blueLivePulse");

    const lines = [
        ...current.map(
            (b) => `${liveEmoji ? `<${liveEmoji.animated ? "a:" : ""}${liveEmoji.name}:${liveEmoji.id}>` : ":blue_circle:"} **${discord.time(startOf(b), discord.TimestampStyles.ShortTime)} ${b.episode.title}**`,
        ),
        ...upcoming.map(
            (b) => `:black_large_square: ${discord.time(startOf(b), discord.TimestampStyles.ShortTime)} ${b.episode.title}`,
        ),
    ];

    if (lines.length > 0) {
        container.addTextDisplayComponents(
            new discord.TextDisplayBuilder().setContent(lines.join("\n")),
        );
    } else {
        container.addTextDisplayComponents(
            new discord.TextDisplayBuilder().setContent("No entries were found."),
        );
    }

    const emoji = await client.getEmoji("favicon");

    const schedButton = new discord.ButtonBuilder()
        .setLabel("Open")
        .setStyle(discord.ButtonStyle.Link)
        .setURL(`${channelConfig.scheduleLink}`);

    if (emoji) {
        schedButton.setEmoji({
            id: emoji.id,
            name: emoji.name,
            animated: emoji.animated,
        })
    };

    container.addSectionComponents(s =>
        s.addTextDisplayComponents(td => td.setContent("Full schedule: "))
            .setButtonAccessory(schedButton)
    );
    container.addSeparatorComponents(s => s.setDivider(true));
    container.addTextDisplayComponents(td => td.setContent(`-# Last updated: ${discord.time(new Date(), discord.TimestampStyles.LongDateShortTime)}`));
    container.addSeparatorComponents(s => s.setDivider(true));
    container.addTextDisplayComponents(td => td.setContent(`**This feature is in beta!** Report any issues on [Github](https://github.com/valbuildr/fansbot), or DM <@1191850547138007132>.`));

    return container;
}

async function refreshSchedules(client: Client<true>): Promise<void> {
    const channel = client.channels.cache.get(process.env.SCHEDULES_CHANNEL_ID!) ?? await client.channels.fetch(process.env.SCHEDULES_CHANNEL_ID!).catch(() => null);

    if (!channel || !channel.isSendable()) {
        return;
    }

    const autoChannels: (keyof typeof allChannels)[] = ["bbc_four", "bbc_two_england", "bbc_one_london", "bbc_news24"];

    for (const chnl of autoChannels) {
        const chnlConf = allChannels[chnl]!;

        const schedule = await fetchSchedule(chnl, new Date());

        if (!schedule) { return; }

        const container = await fmtSchedule(client, schedule, chnlConf);

        const msgId = await readFromStorage("schedules", "messageIds", chnl);

        if (!msgId) {
            const msg = await channel.send({ components: [container], flags: discord.MessageFlags.IsComponentsV2, allowedMentions: { parse: [] } });
            await writeToStorage("schedules", "messageIds", chnl, msg.id);
        } else {
            const msgRef = channel.messages.cache.get(msgId) ?? await channel.messages.fetch(msgId).catch(() => null);

            if (msgRef) {
                await msgRef.edit({ components: [container], flags: discord.MessageFlags.IsComponentsV2 });
            } else {
                const msg = await channel.send({ components: [container], flags: discord.MessageFlags.IsComponentsV2, allowedMentions: { parse: [] } });
                await writeToStorage("schedules", "messageIds", chnl, msg.id);
            }
        }
    }
}

export async function setup(client: Client<true>): Promise<void> {
    refreshSchedules(client);
    setInterval(() => refreshSchedules(client).catch(err => console.error("schedule refresh failed: ", err)), 1000 * 60 * 15);

    console.log("Schedules extension loaded.");
    return;
}