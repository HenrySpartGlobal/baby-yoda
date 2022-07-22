from discord.ext.commands import Cog
from discord.ext.commands import command


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=["hi", "hey", "sup", "hiya", "greetings", "Hi", "Hey", "Sup", "Hiya", "Greetings"])
    async def say_hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
