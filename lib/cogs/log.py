from datetime import datetime

from discord import Embed, message
from discord.ext.commands import Cog
from discord.ext.commands import command


class Log(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(1000527671597486161)
            self.bot.cogs_ready.ready_up("log")

    @Cog.listener()
    async def on_user_update(self, before, after):
        if before.avatar_url != after.avatar_url:
            embed = Embed(title="Display picture Update", description="Avatar change - New image below",
                          colour=after.colour,
                          timestamp=datetime.utcnow())

            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            embed = Embed(title="Member Update", description="Nickname change",
                          colour=after.colour,
                          timestamp=datetime.utcnow())
            # embed.set_thumbnail(url=before.avatar_url)

            fields = [("Before", before.display_name, False), ("After", after.display_name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_member_edit(self, before, after):
        if not after.author.bot:
            pass

    @Cog.listener()
    async def on_member_delete(self, before, after):
        if not after.author.bot:
            pass


def setup(bot):
    bot.add_cog(Log(bot))
