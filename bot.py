import os
import logging
import asyncio
import datetime as dt # Not used for now, remove?

import discord as cord
from discord import app_commands
from discord import FFmpegPCMAudio

import yt_dlp as yt

''' TODO LIST
[ ] Add embed back
[ ] Fix music not playing after stopping (bot doen't reconnect) ??? Some inconsistent issue
[ ] Add queue list maybe?
[ ] Leave after all songs played
[ ] Leave after AFK
[ ] Add priority play command
'''

# XXX Remove after testing
from dotenv import load_dotenv
load_dotenv()
# XXX Remove after testing

# ---- Setup ----

logging.basicConfig(level=logging.INFO)

intents = cord.Intents.default()
intents.voice_states = True

client = cord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# yt-dlp options
YTDL_OPTS = {
    "format": "bestaudio",
    "noplaylist": True,
    "quiet": True,
}

FFMPEG_BEFORE = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
FFMPEG_OPTS = {
    "before_options": FFMPEG_BEFORE,
    "options": "-vn -sn -dn",
}

ytdl = yt.YoutubeDL(YTDL_OPTS)


# ---- Core Logic ----

class Track:
    def __init__(self, info, channel, requester):
        self.info = info
        self.channel = channel
        self.requester = requester

    def create_source(self):
        return FFmpegPCMAudio(self.info["url"], **FFMPEG_OPTS)

    @property
    def title(self):
        return self.info.get("title", "Unknown title")

class MusicPlayer:
    def __init__(self, bot: cord.Client, guild: cord.Guild):
        self.bot = bot
        self.guild = guild
        self.voice: cord.VoiceClient | None = None

        self.queue = asyncio.Queue()
        self.current: Track | None = None

        self.next = asyncio.Event()
        self.task = bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        while True:
            self.next.clear()
            self.current = await self.queue.get()

            if not self.voice or not self.voice.is_connected():
                self.voice = await self.current.channel.connect(self_deaf=True)

            source = self.current.create_source()

            self.voice.play(
                source,
                after=lambda _: self.bot.loop.call_soon_threadsafe(
                    self.next.set
                ),
            )

            await self.next.wait()

    async def stop(self):
        self.queue = asyncio.Queue()
        if self.voice and self.voice.is_connected():
            await self.voice.disconnect()
            self.voice = None


# ---- Player Registry ----

players: dict[int, MusicPlayer] = {}

def get_player(bot: cord.Client, guild: cord.Guild) -> MusicPlayer:
    if guild.id not in players:
        players[guild.id] = MusicPlayer(bot, guild)
    return players[guild.id]


# ---- Slash Commands ----

@tree.command(description="Let the music in tonight")
@app_commands.describe(url="Give life back to music")
async def play(interaction: cord.Interaction, url: str):
    if not interaction.user.voice:
        await interaction.response.send_message(
            "Connect to a voice dumbass",
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True, ephemeral=True)

    try:
        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )
    except yt.utils.DownloadError:
        await interaction.followup.send("Shit url mate")
        return

    player = get_player(interaction.client, interaction.guild)

    track = Track(
        info=info,
        channel=interaction.user.voice.channel,
        requester=interaction.user,
    )

    await player.queue.put(track)

    await interaction.followup.send(
        f"Queued **{track.title}**"
    )

@tree.command(description="Skip that shi")
async def skip(interaction: cord.Interaction):
    player = players.get(interaction.guild.id)

    if not player or not player.voice or not player.voice.is_playing():
        await interaction.response.send_message(
            "Nothing is playing yo",
            ephemeral=True,
        )
        return

    player.voice.stop()
    await interaction.response.send_message(
        "Skipped that shi",
        ephemeral=True,
        )

@tree.command(description="Staaaahp")
async def stop(interaction: cord.Interaction):
    player = players.get(interaction.guild.id)

    if not player:
        await interaction.response.send_message(
            "No shi to staaaahp",
            ephemeral=True,
        )
        return

    await player.stop()
    await interaction.response.send_message(
        "Music yoinked",
        ephemeral=True,
        )


# ---- Events ----

@client.event
async def on_ready():
    await tree.sync()
    logging.info("Logged in as %s", client.user)

    activity = cord.Game("WITH YO BALLS")
    await client.change_presence(activity=activity)


# ---- Entrypoint ----

if __name__ == "__main__":
    client.run(os.getenv("TOKEN"))
