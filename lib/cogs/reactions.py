# allow people to have only 1 specific role at a time

from discord.ext.commands import Cog

# id of emoji: id of the role
colours = {
    "🟢": 1003072600303480892,
    "⚪": 1003072657870295130,
    "🟠": 1003072721401434193
}


class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.reaction_message = await self.bot.get_channel(1003070428614496378).fetch_message(
                1003070709842595890)  # channel, and message to look at
            print(self.reaction_message.content)
            self.bot.cogs_ready.ready_up("reactions")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_message.id:
            role = self.bot.guild.get_role(colours[payload.emoji.name])
            await payload.member.add_roles(role, reason="Colour role reaction")

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_message.id:
            member = self.bot.guild.get_member(payload.user_id)
            role = self.bot.guild.get_role(colours[payload.emoji.name])
            await member.remove_roles(role, reason="Colour role removal")
        pass


def setup(bot):
    bot.add_cog(Reactions(bot))
