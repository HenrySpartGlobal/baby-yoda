from datetime import datetime
from random import choice
from random import randint

from aiohttp import request
from discord import Embed, File, Color
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command
from discord.ext.commands import cooldown
from random_word import Wordnik

wordnik_service = Wordnik()


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
    @command(name="echo", aliases=["say"], description="Make me echo your message")
    # cooldown - 1 allowed every 5 seconds
    @cooldown(1, 5, BucketType.user)
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    # rules
    @command(name="rules", aliases=["rule"], description="List rules")
    async def echo_message(self, ctx):
        file = File("lib/images/InHouseQueue-rules.png", filename="InHouseQueue-rules.png")
        embed = Embed(title="Server rules", color=Color.red())
        embed.set_image(url="attachment://InHouseQueue-rules.png")
        embed.add_field(name="**1. Be respectful**", value="You must respect all users, regardless of your liking towards them. Treat others the way you want to be treated.", inline=False)
        embed.add_field(name="**2. No Inappropriate Language**", value="The use of profanity should be kept to a minimum. However, any derogatory language towards any user is prohibited.", inline=False)
        embed.add_field(name="**3. No spamming**", value="Do not disrupt chat by spamming.", inline=False)
        embed.add_field(name="**4. No pornographic/adult/other NSFW material**", value="This is a community server, NSFW content will not be tolerated.", inline=False)
        embed.add_field(name="**5. No advertisements**", value="We do not tolerate any kind of advertisements, whether it be for other communities or streams. ", inline=False)
        embed.add_field(name="**6. No offensive names and profile pictures**", value="You will be asked to change your name or picture if the staff deems them inappropriate.", inline=False)
        embed.add_field(name="**7. Direct & Indirect Threats**", value="Threats to other users of DDoS, Death, DoX, abuse, and other malicious threats are absolutely prohibited and disallowed.", inline=True)
        embed.add_field(name="**8. Follow the Discord Community Guidelines**", value="You can find them here: https://discordapp.com/guidelines", inline=False)
        embed.add_field(name="\u200b", value="--------------------------------------------------------------------------", inline=True)
        embed.add_field(name="Your presence in this server implies accepting these rules, including all further changes. These changes might be done at any time without notice, it is your responsibility to check for them.", value="\u200b", inline=False)
        await ctx.send(embed=embed, file=file)

    @command(name="use", aliases=["uses"], description="Basic Use")
    async def echo_use(self, ctx):
        file = File("lib/images/InHouseQueue-basic-use.png", filename="InHouseQueue-basic-use.png")
        embed = Embed(title="How to Play", color=Color.red())
        embed.set_image(url="attachment://InHouseQueue-basic-use.png")
        embed.add_field(name="1. Visit one of the Queue Channels", value="Run `/start/` in <#1028006368101277726>", inline=False)
        embed.add_field(name="2. Pick a role", value="Use the buttons to queue up for a role.", inline=False)
        embed.add_field(name="3. Ready up!", value="Once there are 10 players you'll need to ready up - don't worry you will be tagged.", inline=False)
        embed.add_field(name="4. Join the voice channel", value="A voice channel for your team is automatically created. Time to discuss picks and bans!", inline=False)
        embed.add_field(name="5. Create the custom game", value="Players are responsible for creating the custom game and inviting players. Use the lobby text channel to exchange IGN's.", inline=False)
        embed.add_field(name="6. Game over", value="Once the game is over, run `/win` in your specific lobby. This needs needs **6** votes to go through.", inline=False)
        embed.add_field(name="6. Check the leaderboard", value="Your wins are tracked, try `/leaderboard` in <#1027184904372490240>.", inline=False)
        embed.add_field(name="7. Why not use ProDraft?", value="http://prodraft.leagueoflegends.com/ - Is a great addition, provides a competitive vibe and ensures no champion swap madness!", inline=False)
        await ctx.send(embed=embed, file=file)


    @command(name="welcome", aliases=["welcoming"], description="Welcome")
    async def echo_welcome(self, ctx):
        file = File("lib/images/InHouseQueue-welcome.png", filename="InHouseQueue-welcome.png")
        embed = Embed(title="Welcome to In House Queue!", color=Color.red())
        embed.set_image(url="attachment://InHouseQueue-welcome.png")
        embed.add_field(name="Inspired by LoL Champions Queue", value="We want to provide a similar experience to the Official LoL Champions queue. Champions queue is invite only for Pro / Academy players - so this is the next best thing ;)", inline=False)
        embed.add_field(name="Take your game to the next level", value="Our server aims to provide a realistic replica of Champions queue; a Competitive Environment Pro players are using to hone their skills. You too can do the same here.", inline=False)
        embed.add_field(name="Always try your best", value="We understand games can be intense, particularly competitve games. Please keep in mind to keep flame and toxicity to a minimum. Frustration is allowed, but toxicity will not be tolerated.", inline=False)
        embed.add_field(name="Play, learn, repeat", value="Help each other learn and improve - every loss is a lesson.", inline=False)
        embed.add_field(name="\u200b", value="**See you on the rift!**", inline=False)
        await ctx.send(embed=embed, file=file)

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

    @command(name="aebe", aliases=["askaebe"], description="Send Aebe a DM regarding technical questions")
    async def ask_aebe(self, ctx):
        aebe = ctx.guild.get_member(138707252973404160)  # aebes id
        channel = self.bot.get_channel(830504420415504464)  # askaebe channel
        embed = Embed(title=f"New AskAebe request!", colour=ctx.author.colour, timestamp=datetime.utcnow())
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        embed.add_field(name="Source", value=f"New help request in {channel.mention}", inline=False)
        embed.add_field(name="Jump to message", value=f"[Jump]({ctx.message.jump_url})", inline=False)

        await aebe.send(embed=embed)
        await ctx.channel.send(f"Message sent to {aebe.display_name}", delete_after=120)
        # example !aebe "Question"

    @command(name="emoji", aliases=["addemoji"], description="Make an emoji")
    async def save(self, ctx, name: str):
        try:
            url = ctx.message.attachments[0].url
        except IndexError:
            print("Error: No attachment")
            await ctx.send("No attachment")
        else:
            if url[0:26] == "https://cdn.discordapp.com":
                await ctx.message.attachments[0].save('image.jpg')
                with open('image.jpg', 'rb') as f:
                    data = f.read()
                await ctx.guild.create_custom_emoji(name=name, image=data)
                await ctx.send("New Emoji added!")

    @command(name="wordle")
    async def wordle(self, ctx):
        self.log_channel = self.bot.get_channel(1004520092484259961)
        new_word = wordnik_service.get_random_word(
            hasDictionaryDef="true",
            minLength=5,
            maxLength=5
        ).lower()
        await ctx.send("Thanks for starting a game of Wordle. Start guessing <:annieCheeky:590263847923744788> ")
        await self.log_channel.send(f"The answer to the Wordle is {new_word}")

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        grid = ""
        while (guess := (await self.bot.wait_for('message', check=check)).content.lower()) != new_word:
            line = ""
            if len(guess) != 5:
                await ctx.send("That's not even 5 letters <:weird:698658941445472317>")
            else:
                for expected, actual in zip(guess, new_word):
                    if expected == actual:
                        line += ":green_square:"
                    elif expected in new_word:
                        line += ":yellow_square:"
                    else:
                        line += ":black_large_square:"
                grid += f"{line}\n"
                await ctx.send(line)
        grid += ":green_square:" * 5

        await ctx.send(grid)
        await ctx.send("gg ez")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
