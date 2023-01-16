import discord
from discord.ext import commands, tasks
from itertools import cycle


class Tasks(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        self._statuses = cycle(['school sucks :/',
                                "nothing to see here"])
        self.number = 0

    @commands.Cog.listener()
    async def on_ready(self):
        self.change_status.start()
        print("Tasks are ready")

    @tasks.loop(seconds=20)
    async def change_status(self):
        await self._bot.change_presence(
            activity=discord.Game(next(self._statuses)),
            status=discord.Status.online)

def setup(bot):
    bot.add_cog(Tasks(bot))
