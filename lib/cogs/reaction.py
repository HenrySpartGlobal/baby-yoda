# allow people to have multiple roles

from discord.ext.commands import Cog

# id of emoji: id of the role
colours = {
    "🔵": 1003226911016755240,
    "🔴": 1003226952997539922,
    "🟣": 1003226872047485027
}


class Reaction(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.reaction_message = await self.bot.get_channel(1003070428614496378).fetch_message(
                1003226345435836446)  # channel, and message to look for
            print(self.reaction_message.content)
            self.bot.cogs_ready.ready_up("reaction")

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
    bot.add_cog(Reaction(bot))
