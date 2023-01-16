import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta
from pytz import timezone
import pytz

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

class Misc(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    def get_prefix(self, message):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        return prefixes[str(message.guild.id)]

    @commands.Cog.listener()
    async def on_ready(self):
        print("Miscellaneous commands are ready")

    @commands.command(help="Which dumbass made this bot???")
    async def about(self, ctx):
        about_embed = discord.Embed(title="About Testbot", description="", color=discord.Colour.blurple())
        about_embed.add_field(name="Who made this?", value="The idiot behind this garbage is Kyle#0793, "
                                                           "if you have any suggestions or problems dm him!")
        about_embed.add_field(name="Why did he make this?", value="idk i felt bored one day and i had prior "
                                                                  "coding experience so i tried it and this happened")
        await ctx.send(embed=about_embed)

    @commands.command(help="The name of the command is RIGHT THERE")
    async def test(self, ctx):
        await ctx.send(ctx.message.reference.cached_message.content)

    @commands.command()
    async def avatar(self, ctx, member: commands.MemberConverter):
        avatar_embed = discord.Embed(title=f"{member}'s Avatar")
        avatar_embed.set_image(url=member.avatar)
        await ctx.send(embed=avatar_embed)

    @commands.command(help="Gets useful information about a user.")
    async def whois(self, ctx, *, member: commands.MemberConverter):
        permissions = dict(member.guild_permissions)
        permissions = [perm for perm in permissions.keys() if permissions[perm]]
        permissions = ', '.join([str(elem) for elem in permissions])
        permissions = permissions.replace('_', ' ')
        permissions = permissions.title()

        embed = discord.Embed(title=f'{member.name}#{member.discriminator}',
                              description=member.mention,
                              color=discord.Colour.green())
        embed.add_field(name="User ID", value=member.id, inline=False)
        embed.add_field(name='Joined Discord', value=f'<t:{str(int(member.created_at.timestamp()))}>', inline=False)
        embed.add_field(name='Highest Role', value=member.top_role.mention, inline=False)
        embed.add_field(name="User Permissions", value=permissions, inline=False)
        embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar)
        embed.set_thumbnail(url=member.avatar)
        embed.set_footer(icon_url=ctx.author.avatar,
                         text=f'Requested By {ctx.author.name}#{ctx.author.discriminator}')

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if self._bot.user.mentioned_in(message):
            if message.reference is None:
                prefix_embed = discord.Embed(title='',
                                             description=f'The prefix for {message.guild.name} '
                                                         f'is `{self.get_prefix(message)}`',
                                             color=discord.Color.blurple())

                await message.reply(embed=prefix_embed)

    @commands.command(help="Idk its a test command lol")
    async def asdf(self, ctx):
        await ctx.send('Press to interact!',
                       view=Confirm())

    @commands.command(help="because yes")
    async def dogsong(self, ctx):
        await ctx.send("https://www.youtube.com/watch?v=woPff-Tpkns")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def say(self, ctx, *, message):
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Misc(bot))
