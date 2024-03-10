import asyncio  # Import the asyncio library for asynchronous operations
import json  # Import the JSON library for interacting with .json files

config = json.load(open("config.json"))
logpath = config["log-path"]


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

    with open(logpath, "r", encoding="utf-8") as logfile:
        async for log in getlogs(logfile):
            if log[11] == "<":
                not_sent.append(log)
            if len("".join(not_sent)) >= 1500:  # Send logs once length of message is more than 1000
                string = "".join(not_sent)  # Concatenate logs efficiently
                return string

            await asyncio.sleep(0.1)  # Pause briefly between checks
