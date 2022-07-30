from asyncio import sleep
from datetime import datetime, timedelta
from typing import Optional, List
import discord
from better_profanity import profanity
from discord import Embed, Member, Message
from discord.ext.commands import Cog, Greedy, cooldown, BucketType
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

    @command(name="mute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def mute_members(self, ctx, targets: Greedy[Member], minutes: Optional[int], *,
                           reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            unmutes = []

            for target in targets:
                if not self.mute_role in target.roles:
                    if ctx.guild.me.top_role.position > target.top_role.position:
                        roles_ids = ",".join([str(r.id) for r in target.roles])
                        end_time = datetime.utcnow() + timedelta(
                            seconds=minutes * 60) if minutes else None  # seconds=minutes*3600 for minutes, minutes *60

                        db.execute("INSERT INTO mutes VALUES (?, ?, ?)", target.id, roles_ids,
                                   getattr(end_time, "isoformat", lambda: None)())
                        await target.edit(roles=[self.mute_role])

                        embed = Embed(title="Someone Muted", colour=0xDD2222, timestamp=datetime.utcnow())

                        embed.set_thumbnail(url=target.avatar_url)

                        fields = [("Member", f"{target.name} AKA {target.display_name}", False),
                                  ("Muted by", ctx.author.display_name, False),
                                  ("Duration", f"{minutes:,} minutes(s)" if minutes else "Indefinite", False),
                                  ("Reason", reason, False)]

                        for name, value, inline in fields:
                            embed.add_field(name=name, value=value, inline=inline)

                        await self.log_channel.send(embed=embed)

                        if minutes:
                            unmutes.append(target)

                    else:
                        await ctx.send(f"{target.display_name} can't be muted. kekw")

                else:
                    await ctx.send(f"{target.display_name} is already muted")

            await ctx.send("Mute Complete")
            if len(unmutes):
                await sleep(minutes)
                await self.unmute(ctx, targets)

    @mute_members.error
    async def mute_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    async def unmute(self, ctx, targets, reason="Mute time expired."):
        for target in targets:
            if self.mute_role in target.roles:
                role_ids = db.field("SELECT RoleIds FROM mutes WHERE UserID = ?", target.id)
                roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

                db.execute("DELETE FROM mutes WHERE UserID = ?", target.id)
                await target.edit(roles=roles)

                embed = Embed(title="Someone Unmuted", colour=0xDD2222, timestamp=datetime.utcnow())

                embed.set_thumbnail(url=target.avatar_url)

                fields = [("Member", f"{target.name} AKA {target.display_name}", False),
                          ("Reason", reason, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.log_channel.send(embed=embed)

    @command(name="unmute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def unmute_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments is missing.")

        else:
            await self.unmute(ctx, targets, reason=reason)

    @command(name="andre", aliases=["cageandre", "muteandre", "cage"], description="Mutes Andre.")
    @bot_has_permissions(manage_roles=True)
    # Once every 3 hours
    @cooldown(1, 10800, BucketType.guild)
    async def mute(self, ctx):
        guild = ctx.guild
        andre = ctx.guild.get_member(1001955380160647188)
        mutedRole = discord.utils.get(guild.roles, name="Muted")

        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")

            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak=True, send_messages=False, read_message_history=True,
                                              read_messages=True)

        await andre.add_roles(mutedRole)
        await ctx.send("Caged Andre 👮 - He'll be back in 5 minutes.")

        embed = Embed(title=f"Andre caged", colour=0xDD2222, timestamp=datetime.utcnow())

        await self.log_channel.send(embed=embed)
        await sleep(300)
        await andre.remove_roles(mutedRole)
        embed_uncage = Embed(title=f"Andre uncaged after 5 minutes", colour=0xDD2222, timestamp=datetime.utcnow())
        await self.log_channel.send(embed=embed_uncage)

    @command(name="profanity", aliases=["curse", "swears"])
    @has_permissions(manage_guild=True)
    async def add_profanity(self, ctx, *word):
        with open("./data/profanity.txt", "a", encoding="utf-8") as f:
            f.write("".join([f"{w}\n" for w in word]))

        profanity.load_censor_words_from_file("./data/profanity.txt")
        await ctx.send("Word Added")

    @command(name="delprofanity", aliases=["delcurse", "delswears"])
    @has_permissions(manage_guild=True)
    async def remove_profanity(self, ctx, *word):
        with open("./data/profanity.txt", "r", encoding="utf-8") as f:
            stored = [w.strip() for w in f.readlines()]

        with open("./data/profanity.txt", "w", encoding="utf-8") as f:
            f.write("".join([f"{w}\n" for w in stored if w not in word]))

        profanity.load_censor_words_from_file("./data/profanity.txt")
        await ctx.send("Removed Word")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(1000527671597486161)
            self.mute_role = self.bot.guild.get_role(1001901207746531368)  # create a mute role
            self.bot.cogs_ready.ready_up("mod")

    @Cog.listener()
    async def on_message(self, message: Message):
        if not message.author.bot:
            current_prefix = await self.bot.get_prefix(message)
            if isinstance(current_prefix, List):
                current_prefix = current_prefix[2]
            if not str(message.content).startswith(str(current_prefix)):
                if profanity.contains_profanity(message.content):
                    await message.delete()
                    await message.channel.send("You can't use that word here.")


def setup(bot):
    bot.add_cog(Mod(bot))
