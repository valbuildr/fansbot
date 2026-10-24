# BBC Fans Bot (fansbot)

A bot meant to aid in upkeeping the [BBC Fans Discord server](https://discord.gg/BNdm8gmRPN).

## License

Distributed under the MIT License. See [`LICENSE`](./LICENSE) for more information.

## Hosting

1. Download the source code from the [Releases page](https://github.com/valbuildr/fansbot/releases). (You can also get the latest code changes [here](https://github.com/valbuildr/fansbot/archive/refs/heads/main.zip). Expect more bugs with that.)
2. Ensure you have [Bun](https://bun.com) and [Docker/Docker Compose](https://docker.com) installed.
3. Fill out `example.env` and rename it to `.env`.
4. Fill out `compose.example.yml` and rename it to `compose.yml`.
5. Start the database server with `docker compose up`.
6. Install the required packages with Bun. (`bun install`)
7. Run the bot with `bun src/index.ts`.

## Artificial Intelligence

This project uses Artificial Intelligence (AI) as an aid, but not a replacement.

Contributors should also use this mentality, if they choose to use AI.

## Issues

If you have any issues with the software, please open an issue and I will do my best to implement a fix.

## Contributions

Contributors should **always** follow the [Contributor Code of Conduct](./CONTRIBUTOR_COC.md), and the guidance of using AI tools above.

Violating either are grounds for a ban on contributing to any of my projects in the future.
