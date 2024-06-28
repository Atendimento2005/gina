import discord
from discord.ext import commands
from lib.taskmanager import ComposioAgent
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()


# Mock database
user_database = {
    # 'discord_user_id': 'user_email@example.com'
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
            embed = discord.Embed(title="Email Required", description="Please provide your Google email to connect:", color=0xFF0000)
            await discord_channel.send(embed=embed)

            def check(m):
                return m.author == message.author and m.channel == message.channel

            for _ in range(3):
                try:
                    response = await bot.wait_for('message', check=check, timeout=60.0)
                    user_email = response.content.strip()
                    if "@" in user_email and "." in user_email:  # Simple email validation
                        user_database[user_id] = user_email
                        break
                    else:
                        embed = discord.Embed(title="Invalid Email", description="Please enter a valid email address.", color=0xFF0000)
                        await discord_channel.send(embed=embed)
                except asyncio.TimeoutError:
                    embed = discord.Embed(title="Timeout", description="Timeout. Please try again and provide your email promptly.", color=0xFF0000)
                    await discord_channel.send(embed=embed)
                    return
            else:
                embed = discord.Embed(title="Failed", description="Failed to get a valid email after 3 attempts.", color=0xFF0000)
                await discord_channel.send(embed=embed)
                return
        else:
            user_email = user_database[user_id]

        # Proceed with ComposioAgent
        if user_email not in user_agents:
            user_agents[user_email] = ComposioAgent(user_email, discord_channel, bot=bot)

        agent = user_agents[user_email]
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