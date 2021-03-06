from discord.ext import commands


class Convert(commands.Cog):
    def __init__(self, bot):
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
        self.usage = f'Usage: `{bot.config.MAIN.prefix}convert <amount> <unit1> <unit2>`'

    @commands.command(pass_context=True)
    async def convert(self, ctx, amount1, unit1, unit2):
        """Converts length units from meters to a subhuman unit and back"""
        await ctx.send(self._convert(amount1, unit1, unit2))

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
            return f'Allowed units are: {self.units}'
        meters = amount1 * self.to_meter[unit1]
        return f'{amount1} {unit1} = {round(meters / self.to_meter[unit2], 3)} {unit2}'


def setup(bot):
    bot.add_cog(Convert(bot))
