from asyncio import sleep
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from better_profanity import profanity
from discord import Intents
from discord.errors import Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown)
from discord.ext.commands import Context
from discord.ext.commands import when_mentioned_or

from ..db import db

# profanity.load_censor_words_from_file("./data/profanity.txt")

OWNER_IDS = [135811207645888515]
COGS = [path.split("/")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildId = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)


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
        self.ready = False
        self.cogs_ready = Ready()
        # self.guild = None <--- Will be multi server bot so commenting out for now
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=Intents.all()
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

        print("set up complete")

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildId) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
                     ((member.id,) for member in self.guild.members if not member.bot))

        # removes member from database when they leave the server
        to_remove = []
        stored_members = db.column("SELECT UserID FROM exp")
        for id_ in stored_members:
            if not self.guild.get_member(id_):
                to_remove.append(id_)

        db.multiexec("DELETE FROM exp WHERE UserID = ?",
                     ((id_,) for id_ in to_remove))

        db.commit()

    def run(self, version):
        self.VERSION = version

        print("running setup....")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()
        print("Running bot...")
        super().run(self.TOKEN, reconnect=True)

    # warm up message if body is not ready
    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)
            else:
                await ctx.send("I'm still warming up, please wait...")

    async def channel_reminder(self):
        await self.stdout.send("Rules")

    async def on_connect(self):
        print("Baby Yoda has Connected")

    async def on_disconnect(self):
        print("Baby Yoda has Disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        await self.stdout.send(f"An error occurred in '{err}'")
        raise

    async def on_command_error(self, context, exception):
        if any([isinstance(exception, error) for error in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exception, MissingRequiredArgument):
            await context.send("One or more required arguments are missing", delete_after=5)

        elif isinstance(exception, CommandOnCooldown):
            await context.send(
                f"Command on {str(exception.cooldown.type).split('.')[-1]} cool down. Try again in {exception.retry_after / 60:,.0f} minutes")

        elif hasattr(exception, "original"):

            if isinstance(exception.original, Forbidden):
                await context.send("I don't have permissions to do that", delete_after=10)

            else:
                raise exception.original

        else:
            raise exception

    async def on_ready(self):
        print("Baby Yoda bot is ready")
        if not self.ready:
            self.guild = self.get_guild(368493278460379156)
            self.stdout = self.get_channel(1004523022700531792)
            # self.scheduler.add_job(self.channel_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            # uncomment to send something every week
            self.scheduler.start()
            self.update_db()
            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            await self.stdout.send("Baby Yoda Bot is now Online!! Test 11")
            self.ready = True
            print("Bot ready")

            meta = self.get_cog("Meta")
            await meta.set()

        else:
            print("Bot Reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
        pass


bot = Bot()
