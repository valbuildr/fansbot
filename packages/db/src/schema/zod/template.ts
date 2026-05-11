import * as z from "zod";

export const MessageEmbedSchema = z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    color: z.int().optional(),
    author: z.object({
        name: z.string(),
        url: z.string().optional(),
        icon_url: z.string().optional(),
    }).optional(),
    fields: z.array(
        z.object({
            name: z.string(),
            value: z.string(),
            inline: z.boolean().optional().default(false),
        })
    ).optional(),
    footer: z.object({
        text: z.string(),
        icon_url: z.string().optional(),
    }).optional(),
    timestamp: z.string().optional(),
    image: z.object({
        url: z.string(),
    }).optional(),
    thumbnail: z.object({
        url: z.string(),
    }).optional(),
    provider: z.object({
        name: z.string().optional(),
        url: z.string().optional(),
    }).optional(),
});

export const MessageComponentButtonSchema = z.object({
    type: z.literal(2),
    label: z.string().optional(),
    emoji: z.object({
        id: z.string().optional(),
        name: z.string().optional(),
        animated: z.boolean().optional(),
    }).optional(),
    disabled: z.boolean().optional(),
    style: z.literal(5),
    url: z.string()
});

export const MessageComponentRowSchema = z.object({
    type: z.literal(1),
    components: z.array(MessageComponentButtonSchema)
});

export const MessageDataSchema = z.object({
    content: z.string().optional(),
    embeds: z.array(MessageEmbedSchema).optional(),
    components: z.array(MessageComponentRowSchema).optional(),
})

export type MessageEmbed = z.infer<typeof MessageEmbedSchema>;
export type MessageComponentButton = z.infer<typeof MessageComponentButtonSchema>;
export type MessageComponentRow = z.infer<typeof MessageComponentRowSchema>;
export type MessageComponent = MessageComponentRow | MessageComponentButton;
export type MessageData = z.infer<typeof MessageDataSchema>;