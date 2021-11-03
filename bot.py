import os
import openpyxl
import connect4
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from yandex_music import Client

load_dotenv()
bot = commands.Bot(command_prefix=':')
jukebox = Client.from_credentials(os.getenv('LOGIN'), os.getenv('PASS'))
Path('./YMcache/').mkdir(parents=True, exist_ok=True)


@bot.command(help='Let the music play')
async def play(ctx, url: str):
    voice = get(bot.voice_clients, guild=ctx.guild)
    channel = ctx.message.author.voice.channel

    if not voice: 
        await channel.connect() 
        voice = get(bot.voice_clients, guild=ctx.guild)
    
    if channel != voice:
        await voice.move_to(channel)
        voice = get(bot.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        if url == 'likes':
            setlist = jukebox.users_likes_tracks()
            tracks = setlist.fetchTracks()

        else:
            try:
                int(url.split('/')[-1])
                parsed_id = url.split('/')[-1]
                try:
                    int(url.split('/')[-3])
                    parsed_id += ':' + url.split('/')[-3]

                    tracks = jukebox.tracks(track_ids=[parsed_id])
                except Exception:
                    setlist = jukebox.albums_with_tracks(parsed_id)
                    tracks = []
                    for volume in setlist.volumes:
                        tracks += volume

            except Exception:
                await ctx.send('Link seems to be invalid')
                await channel.disconnect()
                return

        await ctx.send('Today we will be talking about:')
        queue_len = len(tracks)
        if queue_len > 5:
            queue_len = 5
        for i in range(queue_len):
            await ctx.send(f'{i}. {tracks[i].artists[0].name} - {tracks[i].title}')

        for track in tracks:
            file_path = f'./YMcache/{track.id}.aac'  # track should be deleted after some time
            track_time = track.duration_ms // 1000

            if not os.path.exists(file_path):
                try:
                    track.download(file_path, 'aac', 128)
                except Exception:
                    try:
                        track.download(file_path)
                    except Exception as e:
                        await ctx.send(f'I failed because {e}')
                        return

            voice.play(FFmpegPCMAudio(file_path))
            voice.is_playing()
            await ctx.send(f'{track.artists[0].name} - {track.title} directly in your voice chat')
            await asyncio.sleep(track_time + 1)

    else:
        await ctx.send('Queue coming soon! (for now just kick the bot)')
        return


@bot.command(help='There is no room for this bot anymore')
async def gtfo(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        if voice.is_playing():
            voice.stop()
        await voice.disconnect()


@bot.command(name='69', help='Funny number')
async def sixty_nine(ctx):
    await ctx.send('Nice!')


@bot.command(name='c4', help='A game for two (enter number 1-7, ping to add opponent)')
async def connect_four(ctx, cont: str):
    if not connect4.game_started(ctx.channel.id):
        connect4.new_game(ctx.channel.id)

    r = openpyxl.load_workbook('save.xlsx')
    sheet = r[str(ctx.channel.id)]           # unload xlsx from memory
    p1 = sheet['A2'].value
    p2 = sheet['B2'].value
    message_author = "'" + str(ctx.author.id)
    if message_author == p2:
        await ctx.send('Next!')
        return
    if p1 == "'0":
        if len(cont) > 21 and cont.split()[0][1] == '@':
            if len(cont) > 26 and cont.split()[1] == '-pass':
                p1 = "'" + cont.split()[1][3:-1]
                p2 = message_author
            else:
                p2 = "'" + cont.split()[1][3:-1]
                p1 = message_author
            sheet.cell(column=1, row=2, value=p1)
            sheet.cell(column=2, row=2, value=p2)
            r.save('save.xlsx')
            await ctx.send('Ready player one')
            return
        sheet.cell(column=1, row=2, value=message_author)
        r.save('save.xlsx')
    elif message_author != p1:
        await ctx.send('Wait a minute, who are you?')
        return

    player_input = int(cont.split()[0]) - 1
    if player_input == 68:
        await ctx.send('Nice!')
        return
    if player_input > 6 or player_input < 0:
        await ctx.end('Try another number 1-7')
        return
    response = connect4.turn(player_input, ctx.channel.id)
    if not response:
        await ctx.send('Column is full')
        return
    await ctx.send(response)

    connect4.end_turn(ctx.channel.id)


@bot.command(help='Clear the table')
async def clear(ctx):
    r = openpyxl.load_workbook('save.xlsx')
    for i in r.worksheets:
        if str(i)[12:-2] == str(ctx.channel.id):
            r.remove(i)
            r.save('save.xlsx')
            await ctx.send('Territory purged')
            return
    await ctx.send('Wow, so empty')


@bot.event
async def on_ready():
    print(f'logged in as {bot.user.name}')


bot.run(os.getenv('TOKEN'))
