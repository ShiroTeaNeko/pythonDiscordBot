import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import os
import random
import requests
import json

startup_extensions = ["Music"]
bot = commands.Bot('!')
bot.remove_command('help')


@bot.event
async def on_ready():
    game = discord.Game('Sleepy | !help')
    await bot.change_presence(status=discord.Status.idle, activity=game)
    print('Bot online')


@bot.event
async def on_message(message):
    if message.content == 'img':
        imgList = os.listdir("./Twitter")  # Creates a list of filenames from your folder

        imgString = random.choice(imgList)  # Selects a random element from the list

        path = "./Twitter/" + imgString  # Creates a string for the path to the file

        await bot.send_file(message.channel, path)  # Sends the image in the channel the command was used

    await bot.process_commands(message)


class Main_Commands():
    def __init__(self, bot):
        self.bot = bot


@bot.command(pass_context=True, no_pm=True)
async def konachan(ctx, tag):
    URL = 'https://konachan.com/post.json'

    page = '1'

    PARAMS = {'page': page, 'tags': tag}

    r = requests.get(url=URL, params=PARAMS)
    print(r.text)
    # data = r.json()

    print(r.url)
    strList = r.content
    list = json.loads(strList)
    randList = random.choice(list)

    if r.text == '[]':
        await ctx.send('pas trouvé')

    await ctx.send(randList["sample_url"])


@bot.command()
async def osu(ctx, username):
    embed = discord.Embed(title='Osu!', description='Voici mes principales stats!', color=0xFF6ECA)

    k = 'Osu_TOKEN'
    u = str(username)

    URLuser = 'https://osu.ppy.sh/api/get_user'


    PARAMS = {'u': u, 'k': k}

    r = requests.get(url=URLuser, params=PARAMS)
    print(r.text)

    print(r.url)
    strList = r.content
    print(strList)
    list = json.loads(strList)
    choix = list[0]

    URLimage = 'http://s.ppy.sh/a/' + choix["user_id"]

    embed.set_thumbnail(url=URLimage)
    embed.set_author(name=u, icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Osu%21Logo_%282015%29.svg/1200px-Osu%21Logo_%282015%29.svg.png')
    embed.add_field(name= 'Date d\'inscription', value=choix["join_date"], inline= True)
    embed.add_field(name='Temps de jeu', value= str(int(choix["total_seconds_played"]) // 3600) + ' h', inline=True)
    embed.add_field(name='Level', value=str(round(float(choix["level"]))), inline=True)
    embed.add_field(name='Précision', value="{0:.2f}".format(float(choix["accuracy"])) + ' %', inline=True)
    embed.add_field(name='Nombres de parties lancées', value=choix["playcount"], inline=False)
    embed.add_field(name='Classement Mondiale', value=choix["pp_rank"], inline=True)
    embed.add_field(name='Classement FR', value=choix["pp_country_rank"], inline=True)


    if r.text == '[]':
        await ctx.send('aucune info')
    await ctx.send(embed=embed)



@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Aide', color=0xFF6ECA)

    embed.add_field(name='!konachan', value='Affiche une image de la premiere page du site Konachan')
    embed.add_field(name='!play + LIEN(youtube)', value='Le Bot est summon sur le salon vocal du joueur qui a écrit '
                                                        'la commande et joue la musique du lien')

    await ctx.author.send(embed=embed)


# @bot.command(pass_context=True)
# async def ping(ctx):
# await ctx.send('pong')


if __name__ == '__main__':
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print(' Extension non chargé {}\n{}'.format(extension, exc))

bot.run('TOKEN')
