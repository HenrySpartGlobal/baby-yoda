from datetime import datetime, timedelta
from typing import Optional
from asyncio import sleep

import discord
from discord import Embed, Member
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, bot_has_permissions

from ..db import db


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.", delete_after=3)

        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position
                        and not target.guild_permissions.administrator):
                    await target.kick(reason=reason)

                    embed = Embed(title="Someone kicked", colour=0xDD2222, timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [("Member", f"{target.name} or {target.display_name}", False),
                              ("Kicked by", ctx.author.display_name, False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)

                else:
                    await ctx.send(f"{target.display_name} could not be kicked.")

            await ctx.send("Kick complete")

    @kick_members.error
    async def kick_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Nice try, you don't have permissions for that.", delete_after=5)

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided"):
        if not len(targets):
            await ctx.send("One or more required arguments are missing", delete_after=5)

        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position
                        and not target.guild_permissions.administrator):
                    await target.ban(reason=reason)

                    embed = Embed(title="Someone banned", colour=0xDD2222, timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [("Member", f"{target.name} or {target.display_name}", False),
                              ("Banned by", ctx.author.display_name, False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)

                else:
                    await ctx.send(f"{target.display_name} can't be banned.", delete_after=5)

            await ctx.send("Ban complete")

    @ban_members.error
    async def ban_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Nice try, you don't have permissions for that.", delete_after=10)  # insert an emoji

    @command(name="clear", aliases=["purge", "delete"])
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 3):
        def _check(message):
            return not len(targets) or message.author in targets

        with ctx.channel.typing():
            await ctx.message.delete()
            deleted = await ctx.channel.purge(limit=limit, check=_check)

            await ctx.send(f"Purging last {len(deleted):,} message(s).", delete_after=5)

    @command(name="mute", description="Mutes the specified user.")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")

        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")

            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak=True, send_messages=False, read_message_history=True,
                                              read_messages=True)

        await member.add_roles(mutedRole, reason=reason)
        await ctx.send(f"Muted {member.mention} for reason {reason}")

        embed = Embed(title=f"{member.display_name} Muted", colour=0xDD2222, timestamp=datetime.utcnow())

        embed.set_thumbnail(url=member.avatar_url)

        fields = [("Member", f"{member.display_name}", False),
                  ("Muted by", ctx.author.display_name, False),
                  ("Reason", reason, False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await self.log_channel.send(embed=embed)

    @command(name="unmute", description="Unmutes a specified user.")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def unmute(self, ctx, member: discord.Member):
        mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

        await member.remove_roles(mutedRole)
        embed = Embed(title=f"{member.display_name} Unmuted", colour=0xDD2222, timestamp=datetime.utcnow())

        embed.set_thumbnail(url=member.avatar_url)

        fields = [("Member", f"{member.display_name}", False),
                  ("Unmuted by", ctx.author.display_name, False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(1000527671597486161)
            self.mute_role = self.bot.guild.get_role(1001591748511928460)
            self.bot.cogs_ready.ready_up("mod")


def setup(bot):
    bot.add_cog(Mod(bot))
