import discord
import os
import json
from discord.ext import commands
import asyncio
import asqlite
import os
import time
import wavelink
from asyncdagpi import Client

start = time.time()

with open('settings.json', mode='r', encoding='utf8') as json_config:
    bot_config = json.load(json_config)

intents = discord.Intents().all()

def get_prefix(bot, message):
    if isinstance(message.channel, discord.TextChannel):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        return prefixes[str(message.guild.id)]
    return 'k!'


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, intents=intents,
                         status=discord.Status.idle)

    async def is_owner(self, user: discord.User):
        if user.id == 468941074245615617:  # Implement your own conditions here
            return True

        # Else fall back to the original
        return await super().is_owner(user)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('Hopefully no bugs this time lol\n')


bot = Bot()

bot.dagpi = Client(bot_config["dagpi token"])

@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid Command Used.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You are missing permissions to run this command.\n"
                       f"If you think this is a mistake, please contact {bot.application_info().owner}.")
    elif isinstance(error, commands.ExtensionNotLoaded):
        await ctx.send("The extension(s) you are trying to unload are currently not loaded.")
    elif isinstance(error, commands.ExtensionAlreadyLoaded):
        await ctx.send("The extension(s) you are trying to load are currently already loaded.")
    elif isinstance(error, commands.ExtensionNotFound):
        await ctx.send("The extension you are trying to load does not exist.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("The command you are trying to call can only be called in a server, not a DM.")
    else:
        embed = discord.Embed(title='An Error Occurred.', description='', colour=discord.Colour.red())
        embed.add_field(name="Error", value=error)
        await ctx.send(embed=embed)


@bot.command(help="Changes the server wide prefix. Can only be run by users "
                  "with the Manage Server permission.", aliases=["changeprefix", "cp"])
@commands.has_permissions(manage_guild=True)
@commands.guild_only()
async def change_prefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    embed = discord.Embed(title="Change Successful", description=f"The server prefix was successfully "
                                                                 f"changed to `{prefix}`.")
    await ctx.send(embed=embed)

@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    loaded_cogs = ''
    if extension != '~':
        bot.load_extension(extension)
        loaded_cogs += f'\U000023eb {extension}'
    else:
        for filename in os.listdir('cogs'):
            if filename.endswith('.py'):
                bot.load_extension(f'cogs.{filename[:-3]}')
                loaded_cogs += f'\U000023eb cogs.{filename[:-3]}\n\n'
        loaded_cogs = loaded_cogs[:-2]
    await ctx.send(loaded_cogs)

@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    unloaded_cogs = ''
    if extension != '~':
        bot.unload_extension(extension)
        unloaded_cogs += f'\U000023ec {extension}'
    else:
        for filename in os.listdir('cogs'):
            if filename.endswith('.py'):
                bot.unload_extension(f'cogs.{filename[:-3]}')
                unloaded_cogs += f'\U000023ec cogs.{filename[:-3]}\n\n'
        unloaded_cogs = unloaded_cogs[:-2]
    await ctx.send(unloaded_cogs)

@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    reload_start = time.time()
    reloaded_cogs = ''
    if extension != '~':
        bot.unload_extension(extension)
        bot.load_extension(extension)
        reloaded_cogs += f'\U0001f502 {extension}'
    else:
        for filename in os.listdir('cogs'):
            if filename.endswith('.py'):
                try:
                    bot.unload_extension(f'cogs.{filename[:-3]}')
                except commands.ExtensionNotLoaded:
                    pass
                bot.load_extension(f'cogs.{filename[:-3]}')
                reloaded_cogs += f'\U0001f501 cogs.{filename[:-3]}\n\n'
        reloaded_cogs = reloaded_cogs[:-2]
    await ctx.message.add_reaction('<a:PO_Check:886375713744252939>')
    reload_end = time.time()
    await ctx.send(f'{reloaded_cogs}\nTook {reload_end - reload_start} to reload all')


for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

os.environ['JISHAKU_NO_UNDERSCORE'] = 'true'
os.environ['COVID_API_KEY'] = '7121ac44b6c84a5886ea9adc657c4bd5'

end = time.time()

print(f'[INFO] Bot startup time is {end - start}')
bot.run(bot_config["token"])
