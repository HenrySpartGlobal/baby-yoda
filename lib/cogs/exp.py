from datetime import datetime, timedelta
from random import randint

from discord.ext.commands import Cog

from ..db import db


class Exp(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_xp(self, message):
        xp, lvl, xplock = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id)

        if datetime.utcnow() > datetime.fromisoformat(xplock):
            await self.add_xp(message, xp, lvl)

    async def add_xp(self, message, xp, lvl):
        xp_to_add = randint(5, 15)
        new_lvl = int(((xp + xp_to_add) // 42) ** 0.55)

        # update db values, once level up, need to wait 2mins to get xp again
        db.execute("UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ?", xp_to_add, new_lvl,
                   (datetime.utcnow() + timedelta(seconds=120)).isoformat(), message.author.id)

        if new_lvl > lvl:
            await message.channel.send(
                f"{message.author.mention}, you reached Level {new_lvl:,}! Get a life <:annieCheeky:590263847923744788> ")
            # await self.levelup_channel.send(f"{message.author.mention}, you reached level {new_lvl:,}! Get a life <:annieCheeky:590263847923744788> ")
            # sends to a specific channel

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            # self.levelup_channel = self.bot.get_channel(123456780)
            # sends to a specific channel
            self.bot.cogs_ready.ready_up("exp")

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_xp(message)


def setup(bot):
    bot.add_cog(Exp(bot))
