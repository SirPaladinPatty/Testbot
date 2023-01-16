import requests
import discord
import os
from discord.ext import commands
from discord.ext.commands import BucketType

class CovidStats(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @commands.command()
    @commands.cooldown(5, 5, BucketType.member)
    async def covid(self, ctx, country):
        result = requests.get(f'https://api.covidactnow.org/v2/country/US.json?apiKey={os.environ["COVID_API_KEY"]}')
        us_covid_stats = result.json()

        covid_embed = discord.Embed(title='COVID-19 Stats',
                                    description=f'**Country:** US\n'
                                                f'**New Cases:** {us_covid_stats["actuals"]["newCases"]}\n'
                                                f'**Confirmed Cases:** {us_covid_stats["actuals"]["cases"]}\n'
                                                f'**Deaths:** {us_covid_stats["actuals"]["deaths"]}')

        await ctx.send(embed=covid_embed)

def setup(bot):
    bot.add_cog(CovidStats(bot))
