import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import os
import random
import requests
import json

startup_extensions = ["konachan"]
startup_extensions = ["Music"]
bot = commands.Bot('!')

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='!help'))
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


class Konachan:

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
            await bot.say('pas trouvé')

        await bot.say(randList["sample_url"])




#@bot.command(pass_context=True)
#async def ping(ctx):
    #await bot.say('pong')



if __name__ == '__main__':
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print(' Extension non chargé {}\n{}'.format(extension, exc))


bot.run('NTIyODI5MjQ3MjMyODY4Mzgz.DxZ21A.yUyBnf89MoJ4lPHBOxkW0AIrCRw')
