from tweepy import OAuthHandler, API
import logging
import discord
import asyncio
import os
from html import unescape
from discord.ext import tasks, commands


class TrumpTwitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.TRUMP_TWITTER
        self.api = self.get_api()
        self.last_id = None
        logging.info('Starting Twitter Stream...')
        self.read_tweets.start()

    def get_api(self):
        auth = OAuthHandler(self.config.consumer_key, self.config.consumer_secret)
        auth.set_access_token(self.config.access_token, self.config.access_secret)
        return API(auth)

    @tasks.loop(minutes=1.0)
    async def read_tweets(self):
        tries = []  # query multiple times
        for i in range(5):
            res = self.api.user_timeline(user_id='25073877', since_id=self.last_id, tweet_mode='extended',
                                         include_rts=False)
            tries.append(res)
            await asyncio.sleep(0.5)

        max_count, x = (0, 0)  # find response with most results, fuck you twitter api
        for i in range(0, len(tries) - 1):
            if len(tries[i]) > max_count:
                max_count, x = len(tries[i]), i

        if self.last_id:  # don't post on first run
            await self.process_tweets(tries[x])  # process the result
        if len(tries[x]) > 0:  # set last_id to newest one
            self.last_id = tries[x][0].id

    async def process_tweets(self, tweets):
        # we have to go through them reversed or they may be posted in wrong order
        for tweet in reversed(tweets):
            if tweet is None:
                continue
            if tweet.user.id != 25073877:  # skip tweets that aren't from god himself
                continue
            if hasattr(tweet, 'retweeted_status') or tweet.full_text.startswith('RT @'):  # filter retweets
                continue
            # logging.info(tweet)
            image = None
            text = unescape(tweet.full_text)
            if 'media' in tweet.entities:
                if tweet.entities['media'][0]['type'] == 'photo':  # only jpeg, no gif/video
                    image = tweet.entities['media'][0]['media_url_https']
                    media_url = tweet.entities['media'][0]['url']  # ex https://t.co/ywU2CEih8b
                    if text.endswith(media_url):  # remove media url from tweet text
                        url_lenght = len(media_url) + 1  # remove the whitespace aswell
                        text = text[:-url_lenght]

            await self.post_tweet(tweet.id_str, tweet.user.name, tweet.created_at, text,
                                  tweet.user.profile_image_url_https, image)

    async def post_tweet(self, id_str, username, created_at, text, avatar, image):
        guild = self.bot.get_guild(int(self.config.guild_id))
        channel = guild.get_channel(int(self.config.channel_id))

        url = 'https://twitter.com/statuses/{}'.format(id_str)

        embed = discord.Embed(description="{}\n\n[Link]({})".format(text, url), color=0x00aced)
        embed.set_author(name=username, url='https://twitter.com/realDonaldTrump', icon_url=avatar)
        embed.set_footer(text=created_at, icon_url='https://abs.twimg.com/icons/apple-touch-icon-192x192.png')
        embed.set_thumbnail(url='https://abs.twimg.com/icons/apple-touch-icon-192x192.png')

        if image:
            embed.set_image(url=image)

        await channel.send(embed=embed)

    def cog_unload(self):
        logging.info('Stopping Twitter Stream...')
        self.read_tweets.cancel()


def setup(bot):
    tw = TrumpTwitter(bot)
    bot.add_cog(tw)


if __name__ == '__main__':
    from config import config

    class Bot:
        def __init__(self):
            self.root_dir = os.path.dirname(os.path.abspath(__file__ + '/..'))
            self.main_test = None
            self.config = config.Config()

    b = Bot()
    t = TrumpTwitter(b)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(t.read_tweets())
