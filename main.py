import discord
import asyncio

TOKEN = "your discord bot token here"
CHANNEL = "your discord channel ID here (as integer)"
LOGPATH = "minecraft log path here"


async def follow(file):
    """Efficiently follows a file, yielding new lines as they are added and retrieves a batch of logs."""

    string = ""
    file.seek(0, 2)

    while True:
        try:
            async def read_line():
                """Wrapper function to make readline awaitable"""
                return file.readline()

            task = asyncio.create_task(read_line())
            line = await asyncio.wait_for(task, timeout=1)

            if "[CHAT]" in line:
                line = line.replace(" [Render thread/INFO]: [CHAT]", "")
                string += line
                if len(string) > 1500:
                    return string

        except asyncio.TimeoutError:
            continue
        await asyncio.sleep(0.1)


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    """Main function that makes program work"""
    print(f"We have logged in as {client.user}")
    await client.change_presence(status=discord.Status.idle,
                                 activity=discord.Activity(
                                     type=discord.ActivityType.watching,
                                     name="latest.log"))  # Slay activity (remove whole this if you don't wanna cringe)
    sent = 0

    while True:
        logs = await follow(open(LOGPATH, "r", encoding="UTF-8"))
        message = f"```{logs}```"
        await client.get_channel(CHANNEL).send(message)
        sent += 1
        print(f"{sent} {'message' if sent == 1 else 'messages'} sent since launch.")


client.run(TOKEN)
