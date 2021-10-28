import os
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from yandex_music import Client

load_dotenv()
bot = commands.Bot(command_prefix=':')
jukebox = Client


@bot.event
async def on_ready():
    print(f'logged in as {bot.user.name}')


@bot.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        await channel.connect()


@bot.command()
async def play(ctx):
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(bot.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        tracks = jukebox.tracks(['3389007:143187'])

        for i, short_track in enumerate(tracks):
            try:
                track = short_track.track if short_track.track else short_track.fetchTrack()
                file_path = f'./.YMcache/{track.id}.mp3'

                try:
                    track.download(file_path)
                except Exception as e:
                    await ctx.send('Error:', e)

                voice.play(FFmpegPCMAudio(file_path, **FFMPEG_OPTIONS))
                voice.is_playing()
                await ctx.send(f'Bot is playing {track.artists[0].name} [{track.album[0].title}] - {track.title}')
            except Exception as e:
                await ctx.send('Error:', e)
    else:
        await ctx.send('Bot is already playing')
        return


@bot.command()
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot has been paused')
    else:
        voice.resume()
        await ctx.send('Bot is playing again')


@bot.command()
async def gtfo(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping...')


bot.run(os.getenv('TOKEN'))
