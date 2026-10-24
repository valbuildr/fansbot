import Client from "../utils/Client";

export default async function getAppEmoji(client: Client<true>, emojiName: string) {
    try {
        const appEmojis = await client.application.emojis.fetch();

        const targetEmoji = appEmojis.find(emoji => emoji.name === emojiName);

        if (targetEmoji) {
            return targetEmoji;
        } else {
            console.log(`Could not find an application emoji named: ${emojiName}`);
        }
    } catch (error) {
        console.error('Failed to fetch application emojis:', error);
    }
}