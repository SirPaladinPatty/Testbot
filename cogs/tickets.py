import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import json
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


# noinspection PyBroadException
class Tickets(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Tickets are ready")

    @commands.command(help=f"Displays info for commands about Testbot's ticket system.")
    async def tickethelp(self, ctx):
        with open("data.json") as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if ctx.author.guild_permissions.administrator or valid_user:

            em = discord.Embed(title="Testbot Tickets Help", description="", color=0x00a8ff)
            em.add_field(name="`.new <message>`",
                         value="This creates a new ticket. Add any words after the command if you'd like to send a "
                               "message when we initially create your ticket.")
            em.add_field(name="`.close`",
                         value="Use this to close a ticket. This command only works in ticket channels.")
            em.add_field(name="`.addaccess <role_id>`",
                         value="This can be used to give a specific role access to all tickets. This command can only "
                               "be run if you have an admin-level role for this bot.")
            em.add_field(name="`.delaccess <role_id>`",
                         value="This can be used to remove a specific role's access to all tickets. This command can "
                               "only be run if you have an admin-level role for this bot.")
            em.add_field(name="`.addpingedrole <role_id>`",
                         value="This command adds a role to the list of roles that are pinged when a new ticket is "
                               "created. This command can only be run if you have an admin-level role for this bot.")
            em.add_field(name="`.delpingedrole <role_id>`",
                         value="This command removes a role from the list of roles that are pinged when a new ticket "
                               "is created. This command can only be run if you have an admin-level role for this "
                               "bot.")
            em.add_field(name="`.addadminrole <role_id>`",
                         value="This command gives all users with a specific role access to the admin-level commands "
                               "for the bot, such as `.addpingedrole` and `.addaccess`. This command can only be run "
                               "by users who have administrator permissions for the entire server.")
            em.add_field(name="`.deladminrole <role_id>`",
                         value="This command removes access for all users with the specified role to the admin-level "
                               "commands for the bot, such as `.addpingedrole` and `.addaccess`. This command can "
                               "only be run by users who have administrator permissions for the entire server.")
            em.set_footer(text="Testbot (code based off of ifisq/discord-ticket-system)")

            await ctx.send(embed=em)

        else:

            em = discord.Embed(title="Testbot Tickets Help", description="", color=0x00a8ff)
            em.add_field(name="`.new <message>`",
                         value="This creates a new ticket. Add any words after the command if you'd like to send a "
                               "message when we initially create your ticket.")
            em.add_field(name="`.close`",
                         value="Use this to close a ticket. This command only works in ticket channels.")
            em.set_footer(text="Poggers (code based off of ifisq/discord-ticket-system)")

            await ctx.send(embed=em)

    @commands.command(hidden=True)
    async def new(self, ctx, *, args=None):
        await self._bot.wait_until_ready()

        if args is None:
            message_content = "Please wait, we will be with you shortly!"

        else:
            message_content = "".join(args)

        with open("data.json") as f:
            data = json.load(f)

        ticket_number = int(data["ticket-counter"])
        ticket_number += 1

        ticket_channel = await ctx.guild.create_text_channel("ticket-{}".format(ticket_number))
        await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)

        for role_id in data["valid-roles"]:
            role = ctx.guild.get_role(role_id)

            await ticket_channel.set_permissions(role, send_messages=True, read_messages=True, add_reactions=True,
                                                 embed_links=True, attach_files=True, read_message_history=True,
                                                 external_emojis=True)

        await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True,
                                             embed_links=True, attach_files=True, read_message_history=True,
                                             external_emojis=True)

        em = discord.Embed(title="New ticket from {}#{}".format(ctx.author.name, ctx.author.discriminator),
                           description="{}".format(message_content), color=0x00a8ff)

        await ticket_channel.send(embed=em)

        pinged_msg_content = ""
        non_mentionable_roles = []

        if data["pinged-roles"]:

            for role_id in data["pinged-roles"]:
                role = ctx.guild.get_role(role_id)

                pinged_msg_content += role.mention
                pinged_msg_content += " "

                if role.mentionable:
                    pass
                else:
                    await role.edit(mentionable=True)
                    non_mentionable_roles.append(role)

            await ticket_channel.send(pinged_msg_content)

            for role in non_mentionable_roles:
                await role.edit(mentionable=False)

        data["ticket-channel-ids"].append(ticket_channel.id)

        data["ticket-counter"] = int(ticket_number)
        with open("data.json", 'w') as f:
            json.dump(data, f)

        created_em = discord.Embed(title="Testbot Tickets",
                                   description="Your ticket has been created at {}".format(ticket_channel.mention),
                                   color=0x00a8ff)

        await ctx.send(embed=created_em)

    @commands.command(hidden=True)
    async def close(self, ctx):
        with open('data.json') as f:
            data = json.load(f)

        if ctx.channel.id in data["ticket-channel-ids"]:

            channel_id = ctx.channel.id

            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and \
                       message.content.lower() == "close"

            confirm_view = Confirm()

            em = await ctx.send(embed=discord.Embed(title="Testbot Tickets",
                                                    description="Are you sure you want to close this ticket?",
                                                    color=0x00a8ff), view=confirm_view)

            await ctx.send(embed=em, view=confirm_view)
            await confirm_view.wait()

            if confirm_view.value is None:
                timeout_embed = discord.Embed(title="Testbot Tickets",
                                              description="You didn't answer in time!",
                                              color=0x00a8ff)
                await ctx.send(embed=timeout_embed, delete_after=15)
                await em.delete()
            elif confirm_view.value:
                await ctx.channel.delete()

                index = data["ticket-channel-ids"].index(channel_id)
                del data["ticket-channel-ids"][index]

                with open('data.json', 'w') as f:
                    json.dump(data, f)
            else:
                await ctx.send("Cancelled.")
                await em.delete()

    @commands.command(hidden=True)
    async def addaccess(self, ctx, role_id=None):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:
            role_id = int(role_id)

            if role_id not in data["valid-roles"]:

                try:
                    role = ctx.guild.get_role(role_id)

                    with open("data.json") as f:
                        data = json.load(f)

                    data["valid-roles"].append(role_id)

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="Testbot Tickets",
                                       description=f"You have successfully added `{role.name}` to the list of roles "
                                                   f"with access "
                                                   "to tickets.", color=0x00a8ff)

                    await ctx.send(embed=em)

                except:
                    em = discord.Embed(title="Testbot Tickets",
                                       description="That isn't a valid role ID. Please try again with a valid role ID.")
                    await ctx.send(embed=em)

            else:
                em = discord.Embed(title="Testbot Tickets", description="That role already has access to tickets!",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="Testbot Tickets",
                               description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    @commands.command(hidden=True)
    async def delaccess(self, ctx, role_id=None):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            try:
                role_id = int(role_id)
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                valid_roles = data["valid-roles"]

                if role_id in valid_roles:
                    index = valid_roles.index(role_id)

                    del valid_roles[index]

                    data["valid-roles"] = valid_roles

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="Testbot Tickets",
                                       description=f"You have successfully removed `{role.name}` from the list "
                                                   f"of roles with "
                                                   "access to tickets.", color=0x00a8ff)

                    await ctx.send(embed=em)

                else:

                    em = discord.Embed(title="Testbot Tickets",
                                       description="That role already doesn't have access to tickets!", color=0x00a8ff)
                    await ctx.send(embed=em)

            except:
                em = discord.Embed(title="Testbot Tickets",
                                   description="That isn't a valid role ID. Please try again with a valid role ID.")
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="Testbot Tickets",
                               description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    @commands.command(hidden=True)
    async def addpingedrole(self, ctx, role_id=None):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            role_id = int(role_id)

            if role_id not in data["pinged-roles"]:

                try:
                    role = ctx.guild.get_role(role_id)

                    with open("data.json") as f:
                        data = json.load(f)

                    data["pinged-roles"].append(role_id)

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="Testbot Tickets",
                                       description=f"You have successfully added `{role.name}` to the list "
                                                   "of roles that get "
                                                   "pinged when new tickets are created!", color=0x00a8ff)

                    await ctx.send(embed=em)

                except:
                    em = discord.Embed(title="Testbot Tickets",
                                       description="That isn't a valid role ID. Please try again with a valid role ID.")
                    await ctx.send(embed=em)

            else:
                em = discord.Embed(title="Testbot Tickets",
                                   description="That role already receives pings when tickets are created.",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="Testbot Tickets",
                               description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    @commands.command(hidden=True)
    async def delpingedrole(self, ctx, role_id=None):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            try:
                role_id = int(role_id)
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                pinged_roles = data["pinged-roles"]

                if role_id in pinged_roles:
                    index = pinged_roles.index(role_id)

                    del pinged_roles[index]

                    data["pinged-roles"] = pinged_roles

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="Testbot Tickets",
                                       description=f"You have successfully removed `{role.name}` from the list "
                                                   f"of roles that "
                                                   "get pinged when new tickets are created.", color=0x00a8ff)
                    await ctx.send(embed=em)

                else:
                    em = discord.Embed(title="Testbot Tickets",
                                       description="That role already isn't getting pinged when new tickets are "
                                                   "created!",
                                       color=0x00a8ff)
                    await ctx.send(embed=em)

            except:
                em = discord.Embed(title="Testbot Tickets",
                                   description="That isn't a valid role ID. Please try again with a valid role ID.")
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="Testbot Tickets",
                               description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    @commands.command(hidden=True)
    @has_permissions(administrator=True)
    async def addadminrole(self, ctx, role_id=None):
        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            data["verified-roles"].append(role_id)

            with open('data.json', 'w') as f:
                json.dump(data, f)

            em = discord.Embed(title="Testbot Tickets",
                               description=f"You have successfully added `{role.name}` to the list "
                                           f"of roles that can run "
                                           "admin-level commands!", color=0x00a8ff)
            await ctx.send(embed=em)

        except:
            em = discord.Embed(title="Testbot Tickets",
                               description="That isn't a valid role ID. Please try again with a valid role ID.")
            await ctx.send(embed=em)

    @commands.command(hidden=True)
    @has_permissions(administrator=True)
    async def deladminrole(self, ctx, role_id=None):
        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            admin_roles = data["verified-roles"]

            if role_id in admin_roles:
                index = admin_roles.index(role_id)

                del admin_roles[index]

                data["verified-roles"] = admin_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Testbot Tickets",
                                   description=f"You have successfully removed `{role.name}` "
                                               f"from the list of roles that get "
                                               f"pinged when new tickets are created.",
                                   color=0x00a8ff)

                await ctx.send(embed=em)

            else:
                em = discord.Embed(title="Testbot Tickets",
                                   description="That role isn't getting pinged when new tickets are created!",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="Testbot Tickets",
                               description="That isn't a valid role ID. Please try again with a valid role ID.")
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Tickets(bot))
