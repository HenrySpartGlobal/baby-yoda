from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase

PREFIX = "+"
OWNER_IDS = [135811207645888515]


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        # self.guild = None <--- Will be multi server bot so commenting out for now
        self.scheduler = AsyncIOScheduler()

        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS)

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

    async def on_ready(self):
        print("Baby Yoda bot is ready")
        if not self.ready:
            self.ready = True
            print("Bot ready")
        else:
            print("Bot Reconnected")

    async def on_message(self, message):
        pass


bot = Bot()
