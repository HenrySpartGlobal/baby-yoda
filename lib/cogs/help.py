from typing import Optional

from discord import Embed
from discord.utils import get
from discord.ext.commands import Cog
from discord.ext.commands import command


def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])

    params = []

    return f"``````"




class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        embed = Embed(title=f"`{command}`",
                      description=syntax(command),
                      colour=ctx.author.colour)
        embed.add_field(name="Command description", value=command.help)

    @command(name="help")
    async def show_help(self, ctx, cmd: Optional[str]):
        """Shows this message"""
        if cmd is None:
            pass
        else:
            if command := get(self.bot.commands, name=cmd):
                await self.cmd_help(ctx, command)

            else:
                await ctx.send("That command odes not exist")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("help")


def setup(bot):
    bot.add_cog(Help(bot))
