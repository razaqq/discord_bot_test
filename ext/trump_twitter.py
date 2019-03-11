from twitter import TwitterStream, OAuth, Twitter
from dataclasses import dataclass
import logging
import discord
import json
import asyncio


@dataclass
class Tweet:
    id: str
    name: str
    time: str
    text: str
    avatar: str
    image: str

    def __str__(self):
        s = '{} | {}: "{}"'.format(self.time, self.name, self.text)
        return s


class TrumpTwitter:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config(self.bot.root_dir)
        self.twitter = self.setup()
        self.last_id = None

    @staticmethod
    def load_config(root_dir):
        with open(root_dir + '/config/trump_twitter.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    def setup(self):
        auth = OAuth(self.config['access_token'],
                     self.config['access_secret'],
                     self.config['consumer_key'],
                     self.config['consumer_secret'])
        return Twitter(auth=auth)

    async def read_tweets(self):
        await self.bot.wait_until_ready()  # wait until the bot has loaded all exts
        logging.info('Starting Twitter Stream...')

        while True:
            if self.last_id:
                tweets = self.twitter.statuses.user_timeline(user_id='25073877', since_id=self.last_id,
                                                             tweet_mode='extended')
                await self.process_tweets(tweets)
            self.last_id = self.twitter.statuses.user_timeline(user_id='25073877')[0]['id_str']
            await asyncio.sleep(60)

    async def process_tweets(self, tweets):
        for tweet in tweets:
            if tweet is None:
                continue
            if tweet['user']['id'] != 25073877:  # skip tweets that aren't from god himself
                continue
            if 'retweeted_status' in tweet or tweet['full_text'].startswith('RT @'):  # filter retweets
                continue
            logging.info(tweet)
            image = None
            text = tweet['full_text']
            if 'media' in tweet['entities']:
                if tweet['entities']['media'][0]['type'] == 'photo':  # only jpeg, no gif/video
                    image = tweet['entities']['media'][0]['media_url_https']
                    media_url = tweet['entities']['media'][0]['url']  # ex https://t.co/ywU2CEih8b
                    if text.endswith(media_url):  # remove media url from tweet text
                        url_lenght = len(media_url) + 1  # remove the whitespace aswell
                        text = text[:-url_lenght]

            tweet = Tweet(tweet['id_str'],
                          tweet['user']['name'],
                          tweet['created_at'],
                          text,
                          tweet['user']['profile_image_url_https'],
                          image)
            await self.post_tweet(tweet)

    async def post_tweet(self, tweet):
        all_servers = self.bot.servers
        server = discord.utils.get(all_servers, id=self.config['server_id'])
        channel = server.get_channel(self.config['channel_id'])

        url = 'https://twitter.com/statuses/{}'.format(tweet.id)

        embed = discord.Embed(description="{}\n\n[Link]({})".format(tweet.text, url), color=0x00aced)
        embed.set_author(name=tweet.name, url='https://twitter.com/realDonaldTrump', icon_url=tweet.avatar)
        embed.set_footer(text=tweet.time, icon_url='https://abs.twimg.com/icons/apple-touch-icon-192x192.png')
        embed.set_thumbnail(url='https://abs.twimg.com/icons/apple-touch-icon-192x192.png')

        if tweet.image:
            embed.set_image(url=tweet.image)

        await self.bot.send_message(channel, embed=embed)


def setup(bot):
    tw = TrumpTwitter(bot)
    bot.loop.create_task(tw.read_tweets())
    bot.add_cog(tw)
