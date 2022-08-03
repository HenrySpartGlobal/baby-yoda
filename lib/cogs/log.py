from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog


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
        if before.name != after.name:
            embed = Embed(title="Changed Username",
                          colour=after.colour,
                          timestamp=datetime.utcnow())
            embed.set_thumbnail(url=before.avatar_url)

            fields = [("Before", before.name, False), ("After", after.name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

        if before.discriminator != after.discriminator:
            embed = Embed(title="Changed Discriminator",
                          colour=after.colour,
                          timestamp=datetime.utcnow())
            embed.set_thumbnail(url=before.avatar_url)

            fields = [("Before", before.discriminator, False), ("After", after.discriminator, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.log_channel.send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = Embed(title="Changed Display Picture",
                          description="Avatar change - New image below",
                          colour=after.colour,
                          timestamp=datetime.utcnow())

            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            embed = Embed(title="Changed Nickname",
                          colour=after.colour,
                          timestamp=datetime.utcnow())
            embed.set_thumbnail(url=before.avatar_url)

            fields = [("Before", before.display_name, False), ("After", after.display_name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.log_channel.send(embed=embed)

        elif before.roles != after.roles:
            embed = Embed(title="Changed Role",
                          colour=after.colour,
                          timestamp=datetime.utcnow())
            embed.set_thumbnail(url=before.avatar_url)

            fields = [("Before", ", ".join([r.mention for r in before.roles]), False),
                      ("After", ", ".join([r.mention for r in after.roles]), False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            if before.content != after.content:
                embed = Embed(title=f"{after.author.display_name} edited their message",
                              colour=after.author.colour,
                              timestamp=datetime.utcnow())
                embed.set_thumbnail(url=before.author.avatar_url)

                fields = [("Before", before.content, False),
                          ("After", after.content, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            embed = Embed(title=f"{message.author.display_name} deleted their message",
                          colour=message.author.colour,
                          timestamp=datetime.utcnow())
            embed.set_thumbnail(url=message.author.avatar_url)

            fields = [("Content", message.content, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Log(bot))
