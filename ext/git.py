import requests
from urllib import request
from discord.ext import commands
import traceback
import logging


class Gist(commands.Cog):
    def __init__(self, url):
        self.gist_url = url
        self.gist_id = url.split('/')[-1]
        self.api_url = 'https://api.github.com'

    def __repr__(self):
        return '<Gist Object at {0}>'.format(self.gist_url)

    def get_raw_json(self):
        return requests.get('{0}/gists/{1}'.format(self.api_url, self.gist_id)).json()

    def get_file_name(self):
        files = self.get_raw_json()['files']
        for key in files.keys():
            return key

    def get_file_content(self):
        files = self.get_raw_json()['files']
        return dict([(key, files[key]['content']) for key in files.keys()])

    def get_raw_urls(self):
        files = self.get_raw_json()['files']
        raw_urls = {}
        for key in files.keys():
            raw_urls[key] = files[key]['raw_url']
        return raw_urls

    def download_gists(self, dl_dir):
        try:
            raw_urls = self.get_raw_urls()
            for file_name, url in raw_urls.items():
                request.urlretrieve(url, '{}gist_{}'.format(dl_dir, file_name))
            return True
        except Exception as e:
            print(e)
            return False


class GistExt:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addext(self, url=None):
        """
        gets an extension from gist and trys to load it
        check out https://gist.github.com/razaqq/d7cd6135ca9d9c100f1ec4ed620099d3 for an example extension
        """
        if url:
            if url.startswith('https://gist.github.com/'):
                try:
                    g = Gist(url)
                    g.download_gists(self.bot.workdir + '/ext/')
                    ext_name = 'gist_{}'.format(g.get_file_name().split('.')[0])
                    old = False
                    if 'ext.{}'.format(ext_name) in  self.bot.extensions.keys():
                        old = True
                        self.bot.unload_extension('ext.{}'.format(ext_name))
                    self.bot.load_extension('ext.{}'.format(ext_name))
                    if old:
                        await self.bot.say('I updated and reloaded that extension, go try it!')
                    else:
                        await self.bot.say('I added that extension, go try it!')
                except Exception as e:
                    await self.bot.say('wooooops, something went wrong...')
                    await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
            else:
                await self.bot.say('I will only accept urls that start with https://gist.github.com/, fix your shit!')
        else:
            await self.bot.say('please specify gist url')


def setup(bot):
    bot.add_cog(GistExt(bot))


if __name__ == '__main__':
    gist = Gist('https://gist.github.com/razaqq/d7cd6135ca9d9c100f1ec4ed620099d3')
    print(gist.get_file_name().split('.')[0])
    print(gist.download_gists('./test/'))
