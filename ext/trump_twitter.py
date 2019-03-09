from twitter import TwitterStream, OAuth
from dataclasses import dataclass
import logging
import discord
import json


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
        self.tweet_iter = self.setup()

    @staticmethod
    def load_config(root_dir):
        with open(root_dir + '/config/trump_twitter.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    def setup(self):
        auth = OAuth(self.config['access_token'],
                     self.config['access_secret'],
                     self.config['consumer_key'],
                     self.config['consumer_secret'])
        stream = TwitterStream(auth=auth, secure=True)
        return stream.statuses.filter(follow='25073877')

    async def read_tweets(self):
        for tweet in self.tweet_iter:
            if tweet['user']['id'] != 25073877:  # skip tweets that aren't from god himself
                continue
            if 'retweeted_status' in tweet or tweet['text'].startswith('RT @'):  # filter retweets
                continue
            if tweet['truncated']:  # check if tweet is truncated
                image = None
                text = tweet['extended_tweet']['full_text']
                if 'media' in tweet['extended_tweet']['entities']:
                    if tweet['extended_tweet']['entities']['media'][0]['type'] == 'photo':  # only jpeg, no gif/video
                        image = tweet['extended_tweet']['entities']['media'][0]['media_url_https']
                        media_url = tweet['extended_tweet']['entities']['media'][0]['url']  # ex https://t.co/ywU2CEih8b
                        if text.endswith(media_url):  # remove media url from tweet text
                            url_lenght = len(media_url) + 1  # remove the whitespace aswell
                            text = text[:-url_lenght]
            else:
                image = None
                text = tweet['text']
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
