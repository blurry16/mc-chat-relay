import discord  # Import the Discord library for interacting with Discord
import asyncio  # Import the asyncio library for asynchronous operations

TOKEN = "your discord bot token here"
CHANNEL = "your discord channel ID here (as integer)"
LOGPATH = "minecraft log path here"


async def follow(thefile):
    """Efficiently follows a file, yielding new lines as they are added."""

    thefile.seek(0, 2)  # Start reading from the end of the file

    while True:
        try:
            async def read_line():  # Wrapper function to make readline awaitable
                return thefile.readline()

            task = asyncio.create_task(read_line())  # Create a task to read a line
            line = await asyncio.wait_for(task, timeout=1)  # Wait for line with timeout

            if line:  # Yield the line if it's not empty
                yield line

        except asyncio.TimeoutError:
            continue  # Handle timeout gracefully


async def getlogs(logfile):
    """Filters lines from a log file, yielding those containing "[CHAT]"."""

    async for line in follow(logfile):
        if "[CHAT]" in line:
            yield line.replace(" [Render thread/INFO]: [CHAT]", "")  # Clean up chat lines


async def checklen():
    """Retrieves a batch of logs from the Minecraft log file."""

    not_sent = []  # List to store chat logs

    with open(LOGPATH, "r", encoding="utf-8") as logfile:
        async for log in getlogs(logfile):
            not_sent.append(log)
            if len("".join(not_sent)) >= 1500:  # Send logs once length of message is more than 1000
                string = "".join(not_sent)  # Concatenate logs efficiently
                return string

            await asyncio.sleep(0.1)  # Pause briefly between checks


intents = discord.Intents.default()  # Create a default intents object
intents.message_content = True  # Enable the message_content intent for reading messages

client = discord.Client(intents=intents)  # Create a Discord client with specified intents


@client.event  # Decorator for event handling
async def on_ready():  # Function executed when the client connects and is ready
    print(f"We have logged in as {client.user}")  # Print a message indicating successful login
    await client.change_presence(status=discord.Status.idle,
                                 activity=discord.Activity(
                                     type=discord.ActivityType.watching,
                                     name="latest.log"))  # Activity changing
    sent = 0

    while True:  # Infinite loop to continuously check for logs and send messages
        logs = await checklen()  # Call the checklen function to get new logs (presumably from a Minecraft server)
        message = f"```{logs}```"
        await client.get_channel(CHANNEL).send(message)
        sent += 1
        print(f"{sent} messages sent since launch.")


client.run(TOKEN)  # Bot run
