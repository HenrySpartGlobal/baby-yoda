from datetime import datetime
from asyncio import sleep
from glob import glob
from discord import Intents
from discord import Embed, File
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound
from apscheduler.triggers.cron import CronTrigger

from ..db import db

PREFIX = "+"
OWNER_IDS = [135811207645888515]
# COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")] this line for windows
COGS = [path.split("/")[-1][:-3] for path in glob("./lib/cogs/*.py")]


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        # self.guild = None <--- Will be multi server bot so commenting out for now
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all()
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

        print("set up complete")

    def run(self, version):
        self.VERSION = version

        print("running setup....")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()
        print("Running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def channel_reminder(self):
        await self.stdout.send("Rules")

    async def on_connect(self):
        print("Baby Yoda has Connected")

    async def on_disconnect(self):
        print("Baby Yoda has Disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        await self.stdout.send("An error occured")
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
            self.guild = self.get_guild(328696263568654337)
            self.stdout = self.get_channel(999416235609555126)
            # self.scheduler.add_job(self.channel_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            # uncomment to send something every week
            self.scheduler.start()

            # embed = Embed(title="Baby Yoda online!", description="We're live.",
            #               colour=0xFF0000, timestamp=datetime.utcnow())
            # fields = [("Name", "Value", True),
            #           ("Another field", "This field is next to the other one.", True),
            #           ("A non-inline field", "This field will appear on it's own row.", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            # embed.set_author(name="Henry", icon_url=self.guild.icon_url)
            # embed.set_footer(text="This is a footer!")
            # embed.set_thumbnail(url=self.guild.icon_url)
            # embed.set_image(url=self.guild.icon_url)
            # await self.stdout.send(embed=embed)
            #
            # await self.stdout.send(file=File("./data/images/logo.png"))

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            await self.stdout.send("Baby Yoda is now Online, lets go!")
            self.ready = True
            print(" Bot ready")

        else:
            print("Bot Reconnected")

    async def on_message(self, message):
        pass


bot = Bot()
