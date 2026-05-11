# BBC Fans Bot

## Packages and Apps

This is a [Turborepo](https://turborepo.dev/) and has packages and apps. (in `/packages` and `/apps` respectively)

Here's a full list of 'internal' packages used:
| Location | Name | Description
| :-- | :-- | :-- |
| `packages/config` | `@fansbot/config` | Handles server config values. |
| `packages/db` | `@fansbot/db` | Handles database actions. |
| `packages/eslint-config` | `@fansbot/eslint-config` | Shared eslint configs. |
| `packages/snowflake` | `@fansbot/snowflake` | Used for generating snowflakes. |
| `packages/typescript-config` | `@fansbot/typescript-config` | Shared eslint configs. |
| `packages/ui` | `@fansbot/ui` | Shared UI elements between the `docs` and `web` apps. |

And a list of apps:
| Location | Description |
| :-- | :-- |
| `apps/bot` | BBC Fans Bot. |
| `apps/docs` | Documentation on some of Fans Bot's public exports, like it's API. |
| `apps/web` | BBC Fans Bot's web portal. Used to manage cases, message templates, appeals, and more. |

In addition to these packages and apps, a few other things are also required for Fans Bot. All are defined in `docker/compose.base.yml`
| Service Name | Name | Description |
| :-- | :-- | :-- |
| `db` | PostgreSQL | The database. |
| `redis` | Redis | Allows for communication between apps. |

### `compose.base.yml` or `compose.local.yml`?
There's two versions of Docker's compose file in this repo, both located in the `docker` folder.

| Item | `compose.base.yml` | `compose.local.yml` |
| :-- | :-- | :-- |
| Postgres & Redis ports | Does not expose | Exposes, allows for access outside of deployment |
| Automated deployment | Yes | No |

`compose.base.yml` is recommended for production and `compose.local.yml` is recommended for development.