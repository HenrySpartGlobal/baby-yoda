from random import choice
from random import randint

from aiohttp import request
from discord import Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command
from discord.ext.commands import cooldown


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="greet", description="Say Hello to me, I respond back of course!")
    # cooldown - 3 allow in 1 minute
    @cooldown(3, 60, BucketType.guild)
    async def say_hello(self, ctx):
        async with ctx.channel.typing():
            await ctx.send(f"{choice(('Hey,', 'Hi,', 'Sup,', 'Hiya,', 'Greetings,', 'Bonjour', 'Guten tag', 'Hola'))}"
                           f" {ctx.author.mention}")
            await ctx.send(
                f"{choice(('https://tenor.com/view/the-mandalorian-baby-yoda-the-child-star-wars-cute-gif-16181871', 'https://tenor.com/view/baby-yoda-hi-hello-greet-wave-gif-15912640', 'https://tenor.com/view/the-mandalorian-the-child-baby-yoda-cute-wave-gif-16214706', 'https://tenor.com/view/hello-there-baby-yoda-mandolorian-hello-gif-20136589', 'https://tenor.com/view/baby-yoda-gif-19161736'))}")

    # Dice Example command: 1d6 - rolls 1 dice, with the highest value being 6
    @command(name="dice", aliases=["roll"], description="Roll a dice. Example: '1d6' rolls 1 dice with 6 values.")
    @cooldown(1, 3, BucketType.user)
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))

        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]

            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

        else:
            await ctx.send("I can't role that many dice chief <:sadpeepocat:675030215214366781> . Please try a number "
                           " below 25.", delete_after=15)

    # Echo example command: echo Hello World - Deletes the last message and Bot echos the message "Hello World"
    @command(name="echo", aliases=["say"], description=" Make me echo your message")
    # cooldown - 1 allowed every 5 seconds
    @cooldown(1, 5, BucketType.user)
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @command(name="ask", aliases=["asks", "whoasked", "asked", "asked?", "askers"],
             description="Send a random 'No one asked' meme")
    # cooldown - 3 allow in 1 minute
    @cooldown(3, 60, BucketType.user)
    async def who_asked(self, ctx):
        await ctx.send(
            f"{choice(('https://tenor.com/view/meme-dr-fate-dc-didnt-ask-crazy-gif-16034543', 'https://tenor.com/view/miahsgifs-head-turn-spongebob-gif-19234132', 'https://cdn.discordapp.com/attachments/999416235609555126/1003783870912671804/didnt_ask.jpg', 'https://cdn.discordapp.com/attachments/999416235609555126/1003784009169518752/didnt_ask2.png'))}")

    @command(name="kekw", description="A link to the infamous baby yoda kekw video")
    # cooldown - 3 allow in 1 minute
    @cooldown(3, 60, BucketType.user)
    async def kek_video(self, ctx):
        await ctx.send("https://www.youtube.com/watch?v=h1MtnCYQUU0")
        await ctx.send("<:link_mrcrabs:793488850235555920>")

    # Animal facts - +fact {animal}
    @command(name="fact", aliases=["facts"],
             description="Random facts on: Dogs, Cats, Pandas, Foxs, Birds and Koalas")
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

    @command(name="stock", aliases=["price", "stocks"], description="Get the price of a stock")
    async def stock_price(self, ctx, stock: str):
        if (stock := stock.upper()) in stock:
            stock_url = f"https://cryptingup.com/api/assets/{stock}"

            async with request("GET", stock_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    stock_link = data['asset']['quote']['GBP']['price']

                    await ctx.send(f"Price of {stock} is: **£{stock_link:,.2f}**")
                else:
                    await ctx.send(f"I can't find {stock}, you're making shit up.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
