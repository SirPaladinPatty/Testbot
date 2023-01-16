import discord
from discord.ext import commands


class HelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        counter = 0
        embed = discord.Embed(title="Help")
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                if counter % 2 == 0:
                    embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=True)
                else:
                    embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
                counter += 1

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command))
        if command.help is not None:
            embed.add_field(name="Help", value=command.help)
        else:
            embed.add_field(name="Something unexpected happened.",
                            value=f"The requested command, `{command.name}`, doesn't have a description.")
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


class HelpSetup(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(HelpSetup(bot))
