from random import choice
from random import randint

from discord import Embed
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, cooldown)
from aiohttp import request
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello",
             aliases=["hi", "hey", "sup", "hiya", "greetings", "Hi", "Hey", "Sup", "Hiya", "Greetings", "Hola",
                      "Bonjour", "Guten tag", "hola", "bonjour", "guten tag"])
    async def say_hello(self, ctx):
        async with ctx.channel.typing():
            await ctx.send(f"{choice(('Hey,', 'Hi,', 'Sup,', 'Hiya,', 'Greetings,', 'Bonjour', 'Guten tag', 'Hola'))}"
                           f" {ctx.author.mention}")

    # Dice Example command: 1d6 - rolls 1 dice, with the highest value being 6
    @command(name="dice", aliases=["roll"])
    @cooldown(1, 3, BucketType.user)
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))

        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]

            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

        else:
            await ctx.send("I can't role that many dice chief. Please try a number  below 25.")

    # Echo example command: echo Hello World - Deletes the last message and Bot echos the message "Hello World"
    @command(name="echo", aliases=["say"])
    # cooldown - 1 allowed every 5 seconds
    @cooldown(1, 5, BucketType.user)
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @command(name="ask", aliases=["asks", "whoasked", "asked", "asked?"])
    # cooldown - 3 allow in 1 minute
    @cooldown(3, 60, BucketType.user)
    async def who_asked(self, ctx):
        await ctx.send(
            f"{choice(('https://tenor.com/view/meme-dr-fate-dc-didnt-ask-crazy-gif-16034543', 'https://tenor.com/view/miahsgifs-head-turn-spongebob-gif-19234132', 'https://tenor.com/view/didnt-ask-plus-youre-female-gif-20548291', 'https://imgur.com/a/P5Yf5Xw', 'https://imgur.com/a/AYU3IrG'))}")

    @command(name="kekw")
    # cooldown - 3 allow in 1 minute
    @cooldown(3, 60, BucketType.user)
    async def kek_video(self, ctx):
        await ctx.send("https://www.youtube.com/watch?v=h1MtnCYQUU0")

    #@command(name="cageandre", aliases=["muteandre", "andre", "lockandre"])
    # cooldown - 1 allowed 86400 seconds (1 day) for everyone
    #@cooldown(1, 86400, BucketType.guild)
        #async def mute_andre(self, ctx):
    #   await ctx.send("https://www.youtube.com/watch?v=h1MtnCYQUU0")

    # Animal facts - +fact {animal}
    @command(name="fact", aliases=["facts"])
    # cooldown - 3 allow in 1 minute for the entire server
    @cooldown(3, 60, BucketType.guild)
    async def animal_fact(self, ctx, animal: str):
        if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala"):
            fact_url = f"https://some-random-api.ml/facts/{animal}"
            image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

            async with request("GET", image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]

                else:
                    image_link = None

            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(title=f"{animal.title()} fact", description=data["fact"], colour=ctx.author.colour)

                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"API returned with a {response.status} status.")
        else:
            await ctx.send(f"I can't find any facts on {animal.title()}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
