import discord
import openpyxl
from discord.ext import commands
import connect4
from discord import FFmpegPCMAudio
from discord.utils import get
#import youtube_dl as YoutubeDL

TOKEN = open(r'token.txt').readline()
bot = commands.Bot(command_prefix=':')


# @bot.event
# sync def on_ready():
#     print(f'logged in as {bot.user.name}')


# @bot.command(name='count', help='Простой счётчик')               # ????
# async def count(ctx):
#     r = openpyxl.load_workbook('save.xlsx')
#     sheet = r[str(ctx.channel.id)]
#     counter = sheet['D2'].value
#     counter += 1
#     if ctx.message.content == '-clr':
#         counter = 0
#     sheet.cell(column=4, row=2, value=counter)
#     await ctx.send(f'Счёт: {counter}')


@bot.command(name='play', help='Услада для ушей')
async def play(ctx, link: str):
    voice_channel = ctx.author.voice.channel
    await voice_channel.connect()
    voice = get(bot.voice_clients, guild=ctx.guild)
#    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
#    with YoutubeDL(YDL_OPTIONS) as ydl:
#        info = ydl.extract_info(link, download=False)
    musique = link + '.mp3'
    voice.play(FFmpegPCMAudio(musique))


@bot.command(name='stop', help='Сам догадайся что делает эта команда')
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


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


# @bot.command(name='annoy')
# async def annoy(ctx):
#     await ctx.author.voice.connect

bot.run(TOKEN)
