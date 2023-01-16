import discord, asyncio
from discord.ext import commands
import json


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
    return ctx.author.id == 468941074245615617 or ctx.author.guild_permissions.mute_members


def TimeConverter(time):
    if time.endswith("d"):
        return time[:-1] * 24 * 60 * 60
    elif time.endswith('s'):
        return time[:-1]
    elif time.endswith('m'):
        return time[:-1] * 60
    elif time.endswith('mo'):
        return time[:-2] * 24 * 60 * 60 * 30
    elif time.endswith('w'):
        return time[:-1] * 24 * 60 * 60 * 7
    elif time.endswith('h'):
        return time[:-1] * 60 * 60


class ButtonTest(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    def get_mute_role(self, guild_id):
        with open('mute_roles.json', 'r') as f:
            channels = json.load(f)

        return channels[str(guild_id)]

    @commands.command(help="Changes the server wide mute role. By default it is set to nothing. "
                           "Can only be run by users with the Mute Members permission.")
    @commands.check(is_owner)
    async def mute_role(self, ctx, role: commands.RoleConverter):
        with open('mute_roles.json', 'r') as f:
            roles = json.load(f)

        roles[str(role.guild.id)] = role.id

        with open('mute_roles.json', 'w') as f:
            json.dump(roles, f, indent=4)

        role_embed = discord.Embed(title="The Mute Role has been set to", description=role.mention,
                                   color=discord.Color.green())

        await ctx.send(embed=role_embed)

    @commands.command(help="Mutes a user for a specified time. "
                           "Valid time stamps include (for example): `1d`, `3m`, `12h`, etc. "
                           "Can only be run by users with the Mute Members permission.")
    @commands.has_permissions(manage_roles=True)
    @commands.check(is_owner)
    async def temp_mute(self, ctx, member: commands.MemberConverter, time: TimeConverter, *, reason='Unspecified'):
        # We create the view and assign it to a variable so we can wait for it later.
        await ctx.send("Sorry I disabled this command temporarily lol")
        return
        view = Confirm()
        confirmation_embed = discord.Embed(title=f'Successfully muted {member.name}#{member.discriminator}.',
                                           description=f'{member.mention} was muted for {reason}.')
        guild = ctx.guild

        confirmation_message = await ctx.send(embed=discord.Embed(title=f'Are you sure?',
                                                                  description=f'Are you sure you want to '
                                                                              f'mute {member.mention}?'),
                                              view=view)
        # Wait for the View to stop listening for input...
        await view.wait()
        if view.value is None:
            await ctx.send("You didn't answer in time!")
            await confirmation_message.delete()
        elif view.value:
            if not self.get_mute_role(ctx.guild.id):
                for tc in ctx.guild.text_channels:
                    if tc.permissions_for(self._bot.user).send_messages:
                        await tc.send("Please set a muted role for this server!")
            else:
                await ctx.send(embed=confirmation_embed)
                await member.add_roles(guild.get_role(self.get_mute_role(member.guild.id)),
                                       reason=f'{reason} - Muted for {time} seconds by {ctx.author}')
                await confirmation_message.delete()
                await asyncio.sleep(float(time))
                await member.remove_roles(guild.get_role(self.get_mute_role(member.guild.id)),
                                          reason=f"{member}'s mute expired.")
        else:
            await ctx.send("Cancelled.")
            await confirmation_message.delete()


def setup(bot):
    bot.add_cog(ButtonTest(bot))
