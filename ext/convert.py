from discord.ext import commands


class Convert:
    def __init__(self, bot):
        self.bot = bot
        self.units = ['millimeter(s) aka mm',
                      'centimeter(s) aka cm',
                      'meter(s) aka m',
                      'kilometer(s) aka km',
                      'inch aka in',
                      'foot(s) aka ft',
                      'yard(s) aka yd',
                      'mile(s) aka mi']
        self.to_meter = {
            'cm': 0.01,
            'centimeter': 0.01,
            'm': 1,
            'meter': 1,
            'mm': 0.001,
            'millimeter': 0.001,
            'km': 1000,
            'kilometer': 1000,
            'in': 0.0254,
            'inch': 0.0254,
            'ft': 0.3048,
            'foot': 0.3048,
            'yd': 0.9144,
            'yard': 0.9144,
            'mi': 1609.34,
            'mile': 1609.34
        }
        self.usage = 'Usage: {}convert <amount> <unit1> <unit2>'.format(self.bot.config['prefix'])

    @commands.command()
    async def convert(self, amount1, unit1, unit2):
        """Converts length units from meters to a subhuman unit and back"""
        await self.bot.say(self._convert(amount1, unit1, unit2))

    def _convert(self, amount1, unit1, unit2):
        if unit1.endswith('s'):
            unit1 = unit1[:-1]
        if unit2.endswith('s'):
            unit2 = unit2[:-1]
        try:
            amount1 = float(amount1)
        except ValueError:
            return self.usage
        if unit1 not in self.to_meter or unit2 not in self.to_meter:
            return 'Allowed units are: {}'.format(self.units)
        meters = amount1 * self.to_meter[unit1]
        return '{} {} = {} {}'.format(amount1, unit1, round(meters / self.to_meter[unit2], 3), unit2)


def setup(bot):
    bot.add_cog(Convert(bot))


if __name__ == '__main__':
    bot = 1
    c = Convert(bot)
    print(c._convert(6, 'foot', 'inch'))
