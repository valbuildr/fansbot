# BBC Fans Bot (fansbot)

A bot meant to aid in upkeeping the [BBC Fans Discord server](https://discord.gg/BNdm8gmRPN).

## Compatibility

### Python Version

| Version               | Status         |
| :-------------------- | :------------- |
| 3.13.3                | 🔵 Recommended |
| 3.14.x                | 🔴 Unsupported |
| 3.13.x (excl. 3.13.3) | 🟡 Untested    |
| 3.12.x                | 🟡 Untested    |
| 3.11.x                | 🟡 Untested    |
| 3.10.x                | 🟡 Untested    |
| 3.9.x                 | 🟡 Untested    |
| 3.8.x (and lower)     | 🔴 Unsupported |

- 🔵 Recommended: Same as Confirmed.
- 🟢 Confirmed: Tested and confirmed to work, issues will be fixed
- 🟡 Untested: Untested, issues will be fixed
- 🔴 Unsupported: Untested, issues may or may not be fixed

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Hosting

1. Download the source code from the [Releases page](https://github.com/valbuildr/fansbot/releases). (You can also get the latest code changes [here](https://github.com/valbuildr/fansbot/archive/refs/heads/main.zip). Expect more bugs with that.)
2. Ensure you have Python 3.13.3 (or another supported Python version) installed.
3. Fill out `src/config.ex.py` and rename it to `config.py`.
4. (Optional) Create a virtual environment with `python3 -m venv .venv/` and [activate it](https://docs.python.org/3/library/venv.html#how-venvs-work).
5. Install the required packages with pip. (`python3 -m pip install -r requirements.txt`)
6. Run the bot with `python3 src/main.py`.

## Artificial Intelligence

This project uses Artificial Intelligence (AI) as an aid, but not a replacement.

Contributors should also use this mentality, if they choose to use AI.

## Issues

If you have any issues with the software, please first look at the compatibility table above. If you are on a supported platform/software version (this includes untested), please open an issue and I will do my best to implement a fix. (if you know how to code in Python, and you want to take a crack at it, feel free to also open a pull request too!) If you are on an unsupported platform, I will not implement a fix myself. If you create a pull request with code to fix an issue on an unsupported platform, I will probably merge it.

## Contributions

Contributors should **always** follow the [Contributor Code of Conduct](./CONTRIBUTOR_COC.md), and the guidance of using AI tools above.

Violating either are grounds for a ban on contributing to any of my projects in the future.

## Future Features

All planned/proposed new features are on [this](https://github.com/users/valbuildr/projects/2) Github Project.
