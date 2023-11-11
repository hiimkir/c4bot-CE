import os
import datetime as dt
import asyncio
from dotenv import load_dotenv
import discord as cord
from discord import app_commands
from discord import FFmpegPCMAudio
from discord.utils import get
import yt_dlp as yt


load_dotenv()
worker = cord.Client(intents = cord.Intents.default())
coms = cord.app_commands.CommandTree(worker)


@coms.command(description='Let the music in tonight')
@app_commands.describe(url='Give life back to music')
async def play(action, url: str):
    if action.user.voice is None:
        await action.response.send_message(
            'connect to voice dumbass', ephmeral=True
        )
        return

    player = get(action.client.voice_clients, guild=action.guild)
    if player is not None and player.is_playing():
        if url in ['stop', 'stfu', 'kys']:
            await action.response.send_message('as you wish', ephemeral=True)
            player.stop()
            await player.disconnect()
        else:
            await action.response.send_message('stfu im busy', ephmeral=True)
        return

    YT_OPTS = {'format': 'bestaudio', 'noplaylist': 'True'}
    downloader = yt.YoutubeDL(YT_OPTS)
    try:
        info = downloader.extract_info(url, download=False)
    except Exception:
        action.response.send_message('sosamba', ephemeral=True)
        return
    
    if player is None:
        player = await action.user.voice.channel.connect(self_deaf=True)

    B4_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'      
    FFMPEG_OPTS = {'options': '-vn -sn -dn', 'before_options': B4_OPTS}
    player.play(FFmpegPCMAudio(info['url'], **FFMPEG_OPTS))
    
    msg = cord.Embed(
        title=info['title'], url=info['webpage_url'],
        colour=0xFFFFFF, timestamp=dt.datetime.now(),
        description=info['description'][:50]+'...'
    )
    uploader_line = info['uploader'] + '@' + info['upload_date'][6:8] + '/'
    uploader_line += info['upload_date'][4:6] + '/' + info['upload_date'][2:4]
    msg.set_author(name = uploader_line, url=info['channel_url'])
    msg.set_footer(
        text=f'added by {action.user.display_name}',
        icon_url=action.user.avatar.url
    )
    msg.set_image(url=info['thumbnail'])
    await action.response.send_message(
        delete_after=float(info['duration']), embed=msg, ephemeral=False
    )


@worker.event
async def on_ready():
    await coms.sync()
    print(f'logged in as {worker.user.name}')
    stat = cord.Game('WITH YO BALLS', start=dt.datetime(1984, 1, 1))
    await worker.change_presence(activity=stat)


if __name__ == '__main__':
    worker.run(os.getenv('TOKEN'))

