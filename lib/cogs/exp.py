from datetime import datetime, timedelta
from random import randint
from typing import Optional

from discord import Member, Embed
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.menus import MenuPages, ListPageSource

from ..db import db


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=10)

    async def write_page(self, menu, offset, fields=[]):
        len_data = len(self.entries)

        embed = Embed(title="XP Leaderboard",
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.icon_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} of {len_data:,} members")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        return embed

    async def format_page(self, menu, entries):
        offset = (menu.current_page * self.per_page) + 1
        fields = []
        table = (
            "\n".join(
                f"{idx + offset}. {self.ctx.bot.guild.get_member(entry[0]).display_name} (XP: {entry[1]} | Level: {entry[2]})"
                for idx, entry in enumerate(entries)))

        fields.append(("Ranks", table))

        return await self.write_page(menu, offset, fields)


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

    # show level and rank
    @command(name="level")
    async def display_level(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        xp, level = db.record("SELECT XP, Level FROM exp WHERE UserID =?", target.id) or (None, None)

        if level is not None:
            await ctx.send(f"{target.display_name}, is level {level} with {xp:,} XP")
        else:
            await ctx.send(f"I am currently not tracking {target.display_name} in the experience system")

    @command(name="rank")
    async def display_rank(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        ids = db.column("SELECT UserID FROM exp ORDER BY XP DESC")

        try:
            await ctx.send(f"{target.display_name} is rank {ids.index(target.id) + 1} of {len(ids)}")

        except ValueError:
            await ctx.send(f"I am currently not tracking {target.display_name} in the experience system")

    @command(name="leaderboard", aliases=["lb"])
    async def display_leaderboard(self, ctx):
        records = db.records("SELECT UserID, XP, Level FROM exp ORDER BY XP DESC")

        menu = MenuPages(source=HelpMenu(ctx, records),
                         clear_reactions_after=True,
                         timeout=120)

        await menu.start(ctx)

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
