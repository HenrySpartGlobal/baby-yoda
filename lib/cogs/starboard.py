from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog

from ..db import db


class Starboard(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.starboard_channel = self.bot.get_channel(1003340610897457162)
            self.bot.cogs_ready.ready_up("starboard")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        payload.emoji.name = "⭐"
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

        if not message.author.bot and payload.member.id != message.author.id:
            msg_id, stars = db.record("SELECT StarMessageID, Stars FROM starboard WHERE RootMessageID = ?",
                                      message.id) or (None, 0)
            embed = Embed(title="Starred message", colour=message.author.colour, timestamp=datetime.utcnow())
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.add_field(name="Source", value=f"[Jump]({message.jump_url})", inline=False)
            embed.set_footer(text=f"Channel: {message.channel.name}")

            fields = [("Author", message.author.mention, False),
                      ("Content", message.content or "See attachment", False),
                      ("Stars", stars + 1, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            if len(message.attachments):
                embed.set_image(url=message.attachments[0].url)

            if not stars:
                star_message = await self.starboard_channel.send(embed=embed)
                db.execute("INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?,?)",
                           message.id, star_message.id)

            else:
                star_message = await self.starboard_channel.fetch_message(msg_id)
                await star_message.edit(embed=embed)
                db.execute("UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?", message.id)
        else:
            await message.remove_reaction(payload.emoji, payload.member)


def setup(bot):
    bot.add_cog(Starboard(bot))
