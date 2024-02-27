# XKCD Telegram Bot

This bot serves XKCD comics to a Telegram channel in a random sequence. It is designed to provide an alternative way to explore XKCD comics outside the sequential order presented on the official XKCD website.

## Overview

XKCD is a popular webcomic that covers topics like science, technology, programming, and internet culture with a distinctive stick figure drawing style. This bot fetches unread comics randomly from XKCD and posts them to a specified Telegram channel.

## Features

- **Random Comic Selection:** Comics are selected randomly, providing a varied reading experience.
- **Image and Caption Posting:** Both the comic image and its caption are posted. Captions play an important role in xkcd!
- **Batch Posting Capability:** Allows for multiple comics to be posted in a batch.
- **Configurable Post Interval:** Users can set a custom interval range for comic posting. The bot will sleep a random time within the range.

## Setup Instructions

### Requirements

- Docker
- A Telegram bot API token (get it from @BotFather)
- A Telegram user/channel for posting (get it from @userinfobot)

### Deployment

1. Clone this repository.
2. Create a `.env` file containing your Telegram bot API token and the Telegram channel ID. Refer to [`.env.sample`](./.env.sample) to see available environment variables.
3. Use Docker Compose to deploy the bot:

```bash
docker compose up --build -d
```

## Contribution

Contributions to the bot's development are welcome. To contribute, please fork the repository, make your changes, and submit a pull request. You can also open issues for bugs or feature requests.

## License

This project is licensed under the MIT License - see [`LICENSE`](./LICENSE) for details.

## Acknowledgments

- XKCD for the webcomic content.
- The Telegram Bot API.
