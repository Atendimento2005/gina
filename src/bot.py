import discord
from discord.ext import commands
from lib.taskmanager import ComposioAgent
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()


# Mock database
user_database = {
    # 'discord_user_id': 'user_id@example.com'
}

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix=None, intents=intents)
# Dictionary to store user-specific ComposioAgent instances
user_agents = {}

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        command = message.content.replace(f"@{bot.user.name}", "").strip()
        user_id = str(message.author.id)
        discord_channel = message.channel

        # Check if the user is in the mock database
        if user_id not in user_database:
            #Create new account
            user_database[user_id] = message.author.id
            embed = discord.Embed(description="New account has been created!", color=0x00FF00)
            await discord_channel.send(embed=embed)
            
        else:
            user_id = user_database[user_id]

        # Proceed with ComposioAgent
        if user_id not in user_agents:
            user_agents[user_id] = ComposioAgent(user_id, discord_channel, bot=bot)

        agent = user_agents[user_id]
        if not await agent.connect():
            embed = discord.Embed(title="Connection Failed", description="Failed to connect to Composio services.", color=0xFF0000)
            await discord_channel.send(embed=embed)
            return

        if await agent.doTask(command):
            embed = discord.Embed(title="Success", description=f"Task completed successfully for {message.author.name}.", color=0x00FF00)
            await discord_channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Task Failed", description="Failed to complete the task.", color=0xFF0000)
            await discord_channel.send(embed=embed)
            
bot.run(os.environ["DISCORD_BOT_TOKEN"])