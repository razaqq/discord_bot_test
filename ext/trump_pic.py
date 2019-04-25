from discord.ext import commands
import json
import requests
import random


class TrumpPic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config(self.bot.root_dir)

    @staticmethod
    def load_config(root_dir):
        with open(root_dir + '/config/trump_pic.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    @commands.command(pass_context=True)
    async def trumppic(self, ctx, *, query=None):
        if not query:
            i = ImageSearch(self.config['api_key'], self.config['cx'], 'donald+trump', 1, 100)
        else:
            search_query = 'donald+trump'
            for word in query.split(' '):
                search_query += '+{}'.format(word)
            i = ImageSearch(self.config['api_key'], self.config['cx'], search_query, 1, 10)
        img = i.get_image()
        if img:
            await ctx.send(img)
        else:
            await ctx.send('Something went turbowrong, retry')


class ImageSearch:
    def __init__(self, api_key, cx, query, amount, max_query_num):
        self.url = 'https://www.googleapis.com/customsearch/v1?' \
                    'key={}&cx={}&q={}&searchType=image&num={}' \
                    '&imgType=face'.format(api_key, cx, query, amount)
        self.max_query_num = max_query_num

    def get_image(self):
        start = str(random.randint(1, self.max_query_num))
        r = requests.get(self.url + '&start=' + start)
        data = r.json()
        if 'items' in data:
            return data['items'][0]['link']
        else:
            return None


def setup(bot):
    t = TrumpPic(bot)
    bot.add_cog(t)
