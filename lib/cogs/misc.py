from discord.ext.commands import CheckFailure
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

from ..db import db


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="prefix")
    @has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, new: str):
        if len(new) > 5:
            await ctx.send("Prefix too long. Prefix can not be longer than 5 characters in length.", delete_after=15)

        else:
            db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id)
            await ctx.send(f"Prefix set to {new}.")

    @change_prefix.error
    async def change_prefix_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send(
                "You're not important enough to change that - You need manage "
                "server permissions. ",
                delete_after=15)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")


def setup(bot):
    bot.add_cog(Misc(bot))
