import os
import openpyxl
import connect4
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from yandex_music import Client

load_dotenv()
bot = commands.Bot(command_prefix='.')
jukebox = Client.from_credentials(os.getenv('LOGIN'), os.getenv('PASS'))


@bot.command()
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
            tracks = jukebox.users_likes_tracks()
        else:
            tracks = jukebox.tracks(track_ids=[url])

        for track in tracks: 
            file_path = f'./.YMcache/{track.id}.mp3' 
# track should be deleted after some time
            try:
                track.download(file_path)
            except Exception as e:
                await ctx.send(f'Error: {e}')

            voice.play(FFmpegPCMAudio(file_path))
            voice.is_playing()
            await ctx.send(f'Bot is playing {track.artists[0].name} - {track.title}')

    else:
        await ctx.send('Bot is already playing')
        return


@bot.command()
async def gtfo(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        if voice.is_playing():
            voice.stop()
        await voice.disconnect()


@bot.command(name='69', help='Смишное число')
async def sixty_nine(ctx):
    await ctx.send('Nice!')


@bot.command(name='c4', help='Игра для двоих')
async def connect_four(ctx, cont: str):
    if not connect4.game_started(ctx.channel.id):
        connect4.new_game(ctx.channel.id)

    r = openpyxl.load_workbook('save.xlsx')
    sheet = r[str(ctx.channel.id)]           # unload xlsx from memory
    p1 = sheet['A2'].value
    p2 = sheet['B2'].value
    message_author = "'" + str(ctx.author.id)
    if message_author == p2:
        await ctx.send('Следующий!')
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
            await ctx.send('Игра началась')
            return
        sheet.cell(column=1, row=2, value=message_author)
        r.save('save.xlsx')
    elif message_author != p1:
        await ctx.send('Ты вообще кто?')
        return

    player_input = int(cont.split()[0]) - 1
    if player_input == 68:
        await ctx.send('Nice!')
        return
    if player_input > 6 or player_input < 0:
        await ctx.end('Попробуй другое число 1-7')
        return
    response = connect4.turn(player_input, ctx.channel.id)
    if not response:
        await ctx.send('Столбец уже заполнен')
        return
    await ctx.send(response)

    connect4.end_turn(ctx.channel.id)


@bot.command(name='clear', help='Очистить стол')
async def clear(ctx):
    r = openpyxl.load_workbook('save.xlsx')
    for i in r.worksheets:
        if str(i)[12:-2] == str(ctx.channel.id):
            r.remove(i)
            r.save('save.xlsx')
            await ctx.send('Успешно почищено')
            return
    await ctx.send('Чистить нечего')


@bot.event
async def on_ready():
    print(f'logged in as {bot.user.name}')


bot.run(os.getenv('TOKEN'))
