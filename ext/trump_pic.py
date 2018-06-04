from discord.ext import commands

import json
import logging
import requests
import random


class TrumpPic:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config(self.bot.workdir)

    @staticmethod
    def load_config(workdir):
        with open(workdir + '/config/trump_pic.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    @commands.command()
    async def trumppic(self):
        i = ImageSearch(self.config['api_key'], self.config['cx'], 'donald+trump', 1)
        img = i.get_image()
        if img:
            await self.bot.say(img)
        else:
        	await self.bot.say('Something went turbowrong, retry')


class ImageSearch:
    def __init__(self, api_key, cx, query, num):
        self.url = 'https://www.googleapis.com/customsearch/v1?' \
                    'key={}&cx={}&q={}&searchType=image&num={}' \
                    '&imgType=face'.format(api_key, cx, query, num)

    def get_image(self):
        start = str(random.randint(1, 100))
        r = requests.get(self.url + '&start=' + start)
        data = r.json()
        if 'items' in data:
            return data['items'][0]['link']
        else:
            return None


def setup(bot):
    t = TrumpPic(bot)
    bot.add_cog(t)
