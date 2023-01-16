import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import json
import os
import asyncio


# Define a simple View that gives us a confirmation menu
class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False


def is_owner(ctx):
    return ctx.author.id == 468941074245615617 or ctx.author.guild_permissions.manage_guild

class Moderating(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderating commands are ready')

    def get_report_channel(self, guild_id):
        with open('report_channels.json', 'r') as f:
            channels = json.load(f)

        return channels[str(guild_id)]

    @commands.command(help="Changes the server wide report channel. Can only be run by users "
                           "with the Manage Server permission.")
    @commands.check(is_owner)
    @commands.guild_only()
    async def report_channel(self, ctx, channel: commands.TextChannelConverter):
        with open('report_channels.json', 'r') as f:
            channels = json.load(f)

        channels[str(channel.guild.id)] = channel.id

        with open('report_channels.json', 'w') as f:
            json.dump(channels, f, indent=4)

        await ctx.send(f"New reports will now be sent to {channel.mention}")

    @commands.command(cooldown_message="You're sending reports too fast! Please wait!",
                      help="Sends a report to the admins. Can be run by everyone.")
    @commands.cooldown(1, 5, BucketType.member)
    @commands.guild_only()
    async def report(self, ctx, *, message):
        report_channel = ctx.guild.get_channel(self.get_report_channel(str(ctx.guild.id)))
        report_embed = discord.Embed(title=f'{ctx.author.name}#{ctx.author.discriminator} made a report',
                                     description=f'Author ID: {ctx.author.id}',
                                     color=discord.Colour.red())
        report_embed.add_field(name='Report', value=f'```\n{message}\n```')
        await report_channel.send(embed=report_embed)
        await ctx.send('Message Sent (hopefully) Successfully.')

    @commands.command(help="Deletes a specified number of messages. Can only be run by users "
                           "with the Manage Messages permission.")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def clear(self, ctx, amount=5):
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"{amount} messages cleared!", delete_after=3)

    @commands.command(help="Kicks a specified member. Can only be run by users "
                           "with the Kick Member permission.")
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: commands.MemberConverter, *, reason="Unspecified"):
        view = Confirm()
        confirmation_message = await ctx.send(embed=discord.Embed(title=f'Are you sure?',
                                                                  description=f'Are you sure you want'
                                                                              f' to kick {member.mention}?'),
                                              view=view)
        kick_embed = discord.Embed(title=f"Successfully kicked {member}.",
                                   description=f'{member.mention} was kicked for {reason}')

        await view.wait()
        if view.value is None:
            await ctx.send("You didn't answer in time!")
            await confirmation_message.delete()
        elif view.value:
            await member.kick(reason=f"{reason} - Kicked by: {ctx.author}")
            await ctx.send(embed=kick_embed)
            await confirmation_message.delete()
        else:
            await ctx.send("Cancelled.")
            await confirmation_message.delete()

    @commands.command(help="Bans a specified member. Can only be run by users "
                           "with the Ban Members permission. (temp ban is coming ok chill)")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: commands.MemberConverter, *, reason="Unspecified"):
        await member.ban(reason=f"{reason} - Banned by: {ctx.author}")
        await ctx.send(embed=discord.Embed(title=f'{member} was unbanned.',
                                           description=f'{member.mention} was banned by '
                                                       f'{ctx.author.mention} '
                                                       f'for **{reason}**'))

    @commands.command(help="Unbans a specified member. Can only be run by users "
                           "with the Ban Members permission.")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, *, member: discord.User):
        banned_users = await ctx.guild.bans()

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member.name, member.discriminator):
                await ctx.send(embed=discord.Embed(title=f"{user} was unbanned.",
                                                   description=f'{user.mention} was unbanned '
                                                               f'by {ctx.author.mention}'))
                await ctx.guild.unban(user, reason=f'{user} was unbanned by '
                                                   f'{ctx.author}.')
                return

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        view = Confirm()
        shutdown_embed = discord.Embed(title='Are you sure?', description='Bro what did you do now :/',
                                       color=discord.Colour.red())
        confirmation_message = await ctx.send(embed=shutdown_embed, view=view)

        await view.wait()
        if view.value is None:
            await ctx.send("You didn't answer in time!")
            await confirmation_message.delete()
        elif view.value:
            await confirmation_message.edit(embed=discord.Embed(title='Shutdown Successful',
                                                          description='The bot is offline. '
                                                                      '<:off:886371568438087720>',
                                                          color=discord.Colour.dark_grey()), view=None)
            owner = self._bot.get_user(468941074245615617)
            await owner.send('Someone (probably you) shut down the bot btw')
            await self._bot.close()
            os.system(exit())
        else:
            await ctx.send("Cancelled.")
            await confirmation_message.delete()


def setup(bot):
    bot.add_cog(Moderating(bot))
