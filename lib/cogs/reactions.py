from datetime import datetime, timedelta

from discord import Embed, member
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

from lib.db import db

# Here are all the number emotes.
# 0⃣ 1️⃣ 2⃣ 3⃣ 4⃣ 5⃣ 6⃣ 7⃣ 8⃣ 9⃣
numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
           "6⃣", "7⃣", "8⃣", "9⃣", "🔟")


class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.polls = []

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.starboard_channel = self.bot.get_channel(
                1004518096385622096)  # testing channel starboard = 1003340610897457162
            # roles
            self.colours = {
                "🟢": self.bot.guild.get_role(1003072600303480892),
                "⚪": self.bot.guild.get_role(1003072657870295130),
                "🟠": self.bot.guild.get_role(1003072721401434193)
            }
            self.reaction_message = await self.bot.get_channel(760492361343565824).fetch_message(
                1004512871591464980)  # channel, and message to look at needs to be set, or it will error
            # find a random channel/message to set this too
            # testing discord channel = 1003070428614496378 | messageId = 1003070709842595890
            # baby yoda discord channel = 760492361343565824 | messageId = 1004512871591464980
            print(self.reaction_message.content)
            self.bot.cogs_ready.ready_up("reactions")

    @command(name="createpoll", aliases=["poll", "makepoll"])
    # @has_permissions(manage_guild=True)
    # +poll <length is seconds> <Poll title> <Options separated by spaces or merged together with "">
    # Example command
    # +poll 15 "How big is earth?" Big "very big" small medium "very large"
    async def create_poll(self, ctx, hours: int, question: str, *options):  # currently in seconds
        if len(options) > 10:
            await ctx.send("You can only supply a maximum of 10 options")
        else:
            embed = Embed(title=f"Poll",
                          description=question,
                          colour=ctx.author.colour,
                          timestamp=datetime.utcnow())

            fields = [("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
                      ("Instructions", "React to vote!", False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            message = await ctx.send(embed=embed)

            for emoji in numbers[:len(options)]:
                await message.add_reaction(emoji)

            self.polls.append((message.channel.id, message.id))

            self.bot.scheduler.add_job(self.complete_poll, "date",
                                       run_date=datetime.now() + timedelta(seconds=hours * 3600),
                                       args=[message.channel.id, message.id])

    async def complete_poll(self, channel_id, message_id):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)
        most_voted = max(message.reactions, key=lambda r: r.count)

        await message.channel.send(f"Winner is {most_voted.emoji} with {most_voted.count - 1:,} votes!!")
        self.polls.remove((message.channel.id, message.id))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_message.id:
            current_colours = filter(lambda r: r in self.colours.values(), payload.member.roles)
            await payload.member.remove_roles(*current_colours, reason="Colour role reaction")
            await payload.member.add_roles(self.colours[payload.emoji.name], reason="Colour role reaction")
            await self.reaction_message.remove_reaction(payload.emoji, payload.member)
            # poll logi
        elif payload.message_id in (poll[1] for poll in self.polls):
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            for reaction in message.reactions:
                if (not payload.member.bot
                        and payload.member in await reaction.users().flatten()
                        and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)

        # starboard logic
        elif payload.emoji.name == "⭐":
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

        else:
            for message in self.polls:
                if payload.message_id == message.id:
                    for reaction in message.reactions:
                        if member in reaction.users and reaction.emoji != payload.emoji:
                            await message.remove_reaction(reaction.emoji, member)
                    break


def setup(bot):
    bot.add_cog(Reactions(bot))
