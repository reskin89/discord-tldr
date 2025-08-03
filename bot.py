import os
import json
import discord
from discord.ext import commands
from openai import OpenAI
from datetime import datetime, timezone
from typing import List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class TimeFrame(BaseModel):
    start_time: str
    end_time: str

class MessageData(BaseModel):
    timestamp: str
    content: str
    username: str

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

def parse_timeframe_from_natural_language(natural_language: str) -> TimeFrame:
    """
    Use OpenAI to parse start and end times from natural language
    """
    prompt = f"""
    Parse the following natural language request and extract start and end times.
    Return ONLY a JSON object with 'start_time' and 'end_time' fields in ISO format.
    
    Request: {natural_language}
    
    Examples:
    - "last hour" -> {{"start_time": "2024-01-01T10:00:00Z", "end_time": "2024-01-01T11:00:00Z"}}
    - "yesterday" -> {{"start_time": "2024-01-01T00:00:00Z", "end_time": "2024-01-01T23:59:59Z"}}
    - "last 3 hours" -> {{"start_time": "2024-01-01T08:00:00Z", "end_time": "2024-01-01T11:00:00Z"}}
    
    Return only the JSON object:
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that parses natural language time requests into JSON format with start and end times in ISO format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    try:
        # Extract JSON from response
        json_str = response.choices[0].message.content.strip()
        # Remove any markdown formatting if present
        if json_str.startswith('```json'):
            json_str = json_str[7:-3]
        elif json_str.startswith('```'):
            json_str = json_str[3:-3]
        
        timeframe_data = json.loads(json_str)
        return TimeFrame(**timeframe_data)
    except Exception as e:
        print(f"Error parsing timeframe: {e}")
        # Fallback to last hour
        now = datetime.now(timezone.utc)
        one_hour_ago = now.replace(hour=now.hour - 1)
        return TimeFrame(
            start_time=one_hour_ago.isoformat(),
            end_time=now.isoformat()
        )

def convert_messages_to_json(messages: List[discord.Message]) -> List[Dict[str, Any]]:
    """
    Convert Discord messages to JSON format
    """
    message_data = []
    for message in messages:
        # Skip bot messages
        if message.author.bot:
            continue
            
        message_data.append({
            "timestamp": message.created_at.isoformat(),
            "content": message.content,
            "username": message.author.display_name
        })
    
    return message_data

def generate_tldr_summary(messages_data: List[Dict[str, Any]]) -> str:
    """
    Use OpenAI to generate a TLDR summary of the messages
    """
    if not messages_data:
        return "No messages found in the specified time frame."
    
    # Convert messages to a readable format for the prompt
    messages_text = "\n".join([
        f"[{msg['timestamp']}] {msg['username']}: {msg['content']}"
        for msg in messages_data
    ])
    
    prompt = f"""
    Please create a concise TLDR summary of the following Discord channel messages.
    Focus on the main topics, key discussions, and important points.
    Keep the summary under 500 words and make it easy to understand.
    
    Messages:
    {messages_text}
    
    TLDR Summary:
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates concise summaries of Discord conversations."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

@bot.command(name='tldr')
async def tldr_command(ctx, *, natural_language_request: str):
    """
    Generate a TLDR summary of channel messages based on natural language time request
    """
    try:
        # Send initial response
        await ctx.send("🤔 Processing your request...")
        
        # Parse timeframe from natural language
        timeframe = parse_timeframe_from_natural_language(natural_language_request)
        
        # Convert string times to datetime objects
        start_time = datetime.fromisoformat(timeframe.start_time.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(timeframe.end_time.replace('Z', '+00:00'))
        
        # Fetch messages from channel history
        messages = []
        async for message in ctx.channel.history(
            limit=None,
            after=start_time,
            before=end_time
        ):
            messages.append(message)
        
        # Convert messages to JSON format
        messages_data = convert_messages_to_json(messages)
        
        if not messages_data:
            await ctx.send(f"❌ No messages found between {start_time.strftime('%Y-%m-%d %H:%M')} and {end_time.strftime('%Y-%m-%d %H:%M')}")
            return
        
        # Generate TLDR summary
        await ctx.send("📝 Generating summary...")
        summary = generate_tldr_summary(messages_data)
        
        # Create embed for the response
        embed = discord.Embed(
            title="📋 Channel TLDR Summary",
            description=summary,
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📅 Time Frame",
            value=f"From: {start_time.strftime('%Y-%m-%d %H:%M UTC')}\nTo: {end_time.strftime('%Y-%m-%d %H:%M UTC')}",
            inline=False
        )
        embed.add_field(
            name="💬 Messages Analyzed",
            value=str(len(messages_data)),
            inline=True
        )
        embed.add_field(
            name="📊 Original Request",
            value=natural_language_request,
            inline=True
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")
        print(f"Error in tldr command: {e}")

@bot.command(name='tldrhelp')
async def tldrhelp_command(ctx):
    """
    Show help information for TLDR bot
    """
    embed = discord.Embed(
        title="🤖 Discord TLDR Bot Help",
        description="Generate concise summaries of channel messages using natural language time requests.",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="📝 Usage",
        value="`!tldr <time request>`",
        inline=False
    )
    
    embed.add_field(
        name="⏰ Time Request Examples",
        value="""
        • `!tldr last hour`
        • `!tldr yesterday`
        • `!tldr last 3 hours`
        • `!tldr this morning`
        • `!tldr last week`
        • `!tldr today`
        """,
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ How it works",
        value="The bot uses AI to parse your natural language request, fetches messages from the specified time frame, and generates a concise summary of the conversation.",
        inline=False
    )
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    # Get bot token from environment variable
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    if not bot_token:
        print("❌ Error: DISCORD_BOT_TOKEN environment variable not set")
        exit(1)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    print("🚀 Starting Discord TLDR Bot...")
    bot.run(bot_token) 