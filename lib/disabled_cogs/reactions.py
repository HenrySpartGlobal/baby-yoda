from discord.ext.commands import Cog


class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.colours = {
                "🟢": self.bot.guild.get_role(1003072600303480892),
                "⚪": self.bot.guild.get_role(1003072657870295130),
                "🟠": self.bot.guild.get_role(1003072721401434193)
            }
            self.reaction_message = await self.bot.get_channel(1003070428614496378).fetch_message(
                1003070709842595890)  # channel, and message to look at
            print(self.reaction_message.content)
            self.bot.cogs_ready.ready_up("reactions")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_message.id:
            current_colours = filter(lambda r: r in self.colours.values(), payload.member.roles)
            await payload.member.remove_roles(*current_colours, reason="Colour role reaction")
            await payload.member.add_roles(self.colours[payload.emoji.name], reason="Colour role reaction")
            await self.reaction_message.remove_reaction(payload.emoji, payload.member)

    # @Cog.listener()
    # async def on_raw_reaction_remove(self, payload):
    #     if self.bot.ready and payload.message_id == self.reaction_message.id:
    #         member = self.bot.guild.get_member(payload.user_id)
    #         await member.remove_roles(self.colours[payload.emoji.name], reason="Colour role removal")


def setup(bot):
    bot.add_cog(Reactions(bot))
