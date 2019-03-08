import discord

import asyncio
import json
import logging

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy.streaming import StreamListener

import signal
import functools

tweets = []


class TrumpTwitter:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config(self.bot.root_dir)

    @staticmethod
    def load_config(root_dir):
        with open(root_dir + '/config/trump_twitter.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    def start_stream(self):
        auth = OAuthHandler(self.config['consumer_key'], self.config['consumer_secret'])
        auth.set_access_token(self.config['access_token'], self.config['access_secret'])
        api = API(auth)

        listener = StdOutListener()

        stream = Stream(auth=api.auth, listener=listener)
        stream.filter(follow=['25073877'], is_async=True)
        # stream.filter(track=['sandwich'], is_async=True)

    async def check_tweets(self):
        while self.bot.get_cog('TrumpTwitter'):  # check this again
            try:
                tweet_amount = len(tweets)
                i = 0
                while i < tweet_amount:
                    tweet = tweets[i]

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

                    tweet_amount -= 1
                    del tweets[i]

            except Exception as e:
                logging.log(20, e)

            await asyncio.sleep(60)


class Tweet:
    def __init__(self, id_str, name, time, text, avatar, image):
        self.id = id_str
        self.name = name
        self.time = time
        self.text = text
        self.avatar = avatar
        self.image = image

    def __str__(self):
        s = '{} | {}: "{}"'.format(self.time, self.name, self.text)
        return s


class StdOutListener(StreamListener):
    def on_connect(self):
        logging.info("Successfully connected to the twitter api.")

    def on_status(self, status):
        if status.user.id != 25073877:  # from trump?
            return
        if hasattr(status, 'retweeted_status'):  # fuck retweets
            return

        if not status.truncated:
            text = status.text
            image = None
            if 'media' in status.entities:
                if status.entities['media'][0]['type'] == 'photo':  # only jpeg, no gif/video
                    image = status.entities['media'][0]['media_url_https']
                    media_url = status.entities['media'][0]['url']  # ex https://t.co/ywU2CEih8b
                    if text.endswith(media_url):  # remove media url from tweet text
                        url_lenght = len(media_url) + 1  # remove the whitespace aswell
                        text = text[:-url_lenght]
        else:
            text = status.extended_tweet['full_text']
            image = None
            if 'media' in status.extended_tweet['entities']:
                if status.extended_tweet['entities']['media'][0]['type'] == 'photo':  # only jpeg, no gif/video
                    image = status.extended_tweet['entities']['media'][0]['media_url_https']
                    media_url = status.extended_tweet['entities']['media'][0]['url']  # ex https://t.co/ywU2CEih8b
                    if text.endswith(media_url):  # remove media url from tweet text
                        url_lenght = len(media_url) + 1  # remove the whitespace aswell
                        text = text[:-url_lenght]

        tweet = Tweet(status.id_str, status.user.name, status.created_at, text, status.user.profile_image_url_https, image)
        tweets.append(tweet)

        tweet = str(tweet).encode('utf-8')
        logging.info(tweet)

    def on_error(self, error_code):
        if error_code == 420:
            logging.error("420 Enhance Your Calm - We are being rate limited."
                          "Possible reasons: Too many login attempts or running too many copies of the same "
                          "application authenticating with the same credentials")
            return False  # returning False in on_error disconnects the stream
        logging.error(f"Error: {error_code}")
        return True


def setup(bot):
    t = TrumpTwitter(bot)
    t.start_stream()
    bot.loop.create_task(t.check_tweets())
    bot.add_cog(TrumpTwitter(bot))
