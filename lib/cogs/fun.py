from random import choice
from random import randint
from discord.ext.commands import Cog
from discord.ext.commands import command


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello",
             aliases=["hi", "hey", "sup", "hiya", "greetings", "Hi", "Hey", "Sup", "Hiya", "Greetings", "Hola",
                      "Bonjour", "Guten tag", "hola", "bonjour", "guten tag"])
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hey,', 'Hi,', 'Sup,', 'Hiya,', 'Greetings,', 'Bonjour', 'Guten tag', 'Hola'))}"
                       f" {ctx.author.mention}")

    # Dice Example command: 1d6 - rolls 1 dice, with highest value being 6
    @command(name="dice", aliases=["roll"])
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))
        rolls = [randint(1, value) for i in range(dice)]

        await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

    # Echo example command: echo Hello World - Deletes the last message and Bot echos the message "Hello World"
    @command(name="echo", aliases=["say"])
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
