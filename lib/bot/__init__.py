from datetime import datetime
from discord import Intents
from discord import Embed, File
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound

PREFIX = "+"
OWNER_IDS = [135811207645888515]


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        # self.guild = None <--- Will be multi server bot so commenting out for now
        self.scheduler = AsyncIOScheduler()

        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all()
        )

    def run(self, version):
        self.VERSION = version

        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()
        print("Running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("Baby Yoda has Connected")

    async def on_disconnect(self):
        print("Baby Yoda has Disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        channel = self.get_channel(999416235609555126)
        await channel.send("An error occured")
        raise

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            pass
        elif hasattr(exception, "original"):
            raise exception.original

        else:
            raise exception

    async def on_ready(self):
        print("Baby Yoda bot is ready")
        if not self.ready:
            self.ready = True
            self.guild = self.get_guild(328696263568654337)
            print("Bot ready")

            channel = self.get_channel(999416235609555126)
            await channel.send("Bot Online")

            embed = Embed(title="Baby Yoda online!", description="We're live.",
                          colour=0xFF0000, timestamp=datetime.utcnow())
            fields = [("Name", "Value", True),
                      ("Another field", "This field is next to the other one.", True),
                      ("A non-inline field", "This field will appear on it's own row.", False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            embed.set_author(name="Henry", icon_url=self.guild.icon_url)
            embed.set_footer(text="This is a footer!")
            embed.set_thumbnail(url=self.guild.icon_url)
            embed.set_image(url=self.guild.icon_url)
            await channel.send(embed=embed)

            await channel.send(file=File("./data/images/logo.png"))

        else:
            print("Bot Reconnected")

    async def on_message(self, message):
        pass


bot = Bot()
