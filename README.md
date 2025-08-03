# Discord TLDR Bot

A Discord bot that generates concise summaries of channel messages using natural language time requests and OpenAI.

## Features

- 🤖 Natural language time parsing (e.g., "last hour", "yesterday", "last 3 hours")
- 📝 AI-powered TLDR summaries of Discord conversations
- 📅 Flexible time frame selection
- 💬 Processes message content, timestamps, and usernames
- 🎨 Beautiful Discord embeds for responses

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Discord Bot Token
# Get this from https://discord.com/developers/applications
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# OpenAI API Key
# Get this from https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. Enable the following bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - Use Slash Commands
6. Invite the bot to your server using the OAuth2 URL generator

### 4. OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file

## Usage

### Commands

- `!tldr <time request>` - Generate a TLDR summary for the specified time frame
- `!tldrhelp` - Show help information for the TLDR bot

### Time Request Examples

- `!tldr last hour`
- `!tldr yesterday`
- `!tldr last 3 hours`
- `!tldr this morning`
- `!tldr last week`
- `!tldr today`

## How It Works

1. **Natural Language Parsing**: The bot uses OpenAI to parse your natural language time request into start and end times
2. **Message Fetching**: Discord.py's `channel.history()` method retrieves messages from the specified time frame
3. **Data Transformation**: Messages are converted to JSON format with timestamp, content, and username
4. **AI Summary**: OpenAI generates a concise TLDR summary of the conversation
5. **Response**: The bot replies with a beautiful embed containing the summary and metadata

## Running the Bot

```bash
python bot.py
```

## Requirements

- Python 3.13+
- Discord Bot Token
- OpenAI API Key
- Internet connection

## Dependencies

- `discord.py` - Discord bot framework
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `pydantic` - Data validation

## License

MIT License
