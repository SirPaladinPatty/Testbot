import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta
from pytz import timezone
import pytz

class Welcome(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    def get_welcome_channel(self, id):
        with open('welcome_channels.json', 'r') as f:
            channels = json.load(f)

        try:
            return channels[str(id)]
        except KeyError:
            return False

    @commands.Cog.listener()
    async def on_ready(self):
        print('Welcoming Commands are ready')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print("detected that bot joined guild")
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(guild.id)] = 'k!'

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if int(guild.id) != 336642139381301249:
            if not self.get_welcome_channel(guild.id):
                for tc in guild.text_channels:
                    if tc.permissions_for(self._bot.user).send_messages:
                        await tc.send("Please set a welcome channel for this server!")
            else:
                channel = guild.get_channel(self.get_welcome_channel(guild.id))
                await channel.send(f'Welcome {member}! You are our {guild.member_count}th member! '
                                   f'They joined <t:{str(int(datetime.now(tz=timezone("US/Pacific")).timestamp()))}>.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        if int(guild.id) != 336642139381301249:
            if not self.get_welcome_channel(guild.id):
                for tc in guild.text_channels:
                    if tc.permissions_for(self._bot.user).send_messages:
                        await tc.send("Please set a welcome channel for this server!")
        else:
            channel = guild.get_channel(self.get_welcome_channel(guild.id))
            if channel is None:
                return
            await channel.send(f'{member.name}#{member.discriminator} left. :broken_heart:')

    @commands.command(help="Changes the server wide welcome channel. By default it is set to nothing. "
                           "Can only be run by users with the Manage Server permission.")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def welcome_channel(self, ctx, channel: commands.TextChannelConverter):
        with open('welcome_channels.json', 'r') as f:
            channels = json.load(f)

        channels[str(channel.guild.id)] = channel.id

        with open('welcome_channels.json', 'w') as f:
            json.dump(channels, f, indent=4)

        await ctx.send(f"Welcome Channel set to {channel.mention}")


def setup(bot):
    bot.add_cog(Welcome(bot))
