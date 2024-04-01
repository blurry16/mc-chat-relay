import discord  # Import the Discord library for interacting with Discord
from mc import checklen, config  # Import the checklen function and config object from the mc module


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
        await client.get_channel(config["channel"]).send(message)
        sent += 1
        print(f"{sent} messages sent since launch.")


client.run(config["token"])  # Bot run
