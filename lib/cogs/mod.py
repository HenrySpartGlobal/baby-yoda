from asyncio import sleep
from datetime import datetime, timedelta
from re import search
from typing import Optional

import discord
# from better_profanity import profanity
from discord import Embed, Member, Message
from discord.ext.commands import CheckFailure
from discord.ext.commands import Cog, Greedy, cooldown, BucketType
from discord.ext.commands import command, has_permissions, bot_has_permissions

from ..db import db


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

        # regex to find if a message contains a link
        self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(" \
                         r"\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".," \
                         r"<>?«»“”‘’])) "

        # list of channel ids that are not allowed links or images
        self.no_links = ()
        self.no_images = ()

    async def kick_members(self, message, targets, reason):
        for target in targets:
            if (message.guild.me.top_role.position > target.top_role.position
                    and not target.guild_permissions.administrator):
                await target.kick(reason=reason)

                embed = Embed(title="Someone kicked", colour=0xDD2222, timestamp=datetime.utcnow())

                embed.set_thumbnail(url=target.avatar_url)

                fields = [("Member", f"{target.name} or {target.display_name}", False),
                          ("Kicked by", message.author.display_name, False),
                          ("Reason", reason, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.log_channel.send(embed=embed)

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.", delete_after=10)

        else:
            await self.kick_members(ctx.message, targets, reason)
            await ctx.send("Kick complete")

    @kick_command.error
    async def kick_command_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Nice try, you don't have permissions for that <:OMEGAHERNY:508729267249610779>",
                           delete_after=10)

    async def ban_members(self, message, targets, reason):
        for target in targets:
            if (message.guild.me.top_role.position > target.top_role.position
                    and not target.guild_permissions.administrator):
                await target.ban(reason=reason)

                embed = Embed(title="Someone banned", colour=0xDD2222, timestamp=datetime.utcnow())

                embed.set_thumbnail(url=target.avatar_url)

                fields = [("Member", f"{target.name} or {target.display_name}", False),
                          ("Banned by", message.author.display_name, False),
                          ("Reason", reason, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.log_channel.send(embed=embed)

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided"):
        if not len(targets):
            await ctx.send("One or more required arguments are missing", delete_after=10)

        else:
            await self.ban_members(ctx.message, targets, reason)
            await ctx.send("Ban complete")

    @ban_command.error
    async def ban_command_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Nice try, you don't have permissions for that <:OMEGAHERNY:508729267249610779>",
                           delete_after=10)  # insert an emoji

    @command(name="clear", aliases=["purge", "delete"])
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 3):  # default amount to clear
        def _check(message):
            return not len(targets) or message.author in targets

        with ctx.channel.typing():
            await ctx.message.delete()
            deleted = await ctx.channel.purge(limit=limit, check=_check)

            await ctx.send(f"✅ Purging last {len(deleted):,} message(s).", delete_after=10)

    async def mute_members(self, message, targets, minutes, reason):
        unmutes = []

        for target in targets:
            if not self.mute_role in target.roles:
                if message.guild.me.top_role.position > target.top_role.position:
                    roles_ids = ",".join([str(r.id) for r in target.roles])
                    end_time = datetime.utcnow() + timedelta(
                        seconds=minutes * 60) if minutes else None  # seconds=minutes*3600 for hours, minutes *60

                    db.execute("INSERT INTO mutes VALUES (?, ?, ?)", target.id, roles_ids,
                               getattr(end_time, "isoformat", lambda: None)())
                    await target.edit(roles=[self.mute_role])

                    embed = Embed(title="Someone Muted", colour=0xDD2222, timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [("Member", f"{target.name} AKA {target.display_name}", False),
                              ("Muted by", message.author.display_name, False),
                              ("Duration", f"{minutes:,} minutes(s)" if minutes else "Indefinite", False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)

                    if minutes:
                        unmutes.append(target)
        return unmutes

    @command(name="mute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def mute_command(self, ctx, targets: Greedy[Member], minutes: Optional[int], *,
                           reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.", delete_after=10)

        else:
            unmutes = await self.mute_members(ctx.message, targets, minutes, reason)
            await ctx.send("Mute Complete")
            if len(unmutes):
                await sleep(minutes)
                await self.unmute_members(ctx, targets)

    @mute_command.error
    async def mute_command_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Nice try, you don't have permissions for that <:OMEGAHERNY:508729267249610779>",
                           delete_after=10)

    async def unmute_members(self, guild, targets, reason="Mute time expired."):
        for target in targets:
            if self.mute_role in target.roles:
                role_ids = db.field("SELECT RoleIDs FROM mutes WHERE UserID = ?", target.id)
                roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

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
    async def unmute_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments is missing.", delete_after=10)

        else:
            await self.unmute_members(ctx.guild, targets, reason=reason)

    @command(name="andre", aliases=["cageandre", "muteandre", "cage"], description="Mutes Andre.")
    @bot_has_permissions(manage_roles=True)
    # Once every 3 hours
    @cooldown(1, 10800, BucketType.user)
    async def mute(self, ctx):
        guild = ctx.guild
        andre = ctx.guild.get_member(600461101788037163)
        mutedRole = discord.utils.get(guild.roles, name="Muted")
        endtime = datetime.now() + timedelta(minutes=5)

        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")

            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak=True, send_messages=False, read_message_history=True,
                                              read_messages=True)

        await andre.add_roles(mutedRole)
        await ctx.send(f"Caged Andre - He'll be back at {endtime.strftime('%H:%M:%S')} <:andreTears:963839778242043914>")

        embed = Embed(title=f"Andre caged", colour=0xDD2222, timestamp=datetime.utcnow())

        await self.log_channel.send(embed=embed)
        await sleep(300)
        await andre.remove_roles(mutedRole)
        embed_uncage = Embed(title=f"Andre uncaged after 5 minutes", colour=0xDD2222, timestamp=datetime.utcnow())
        await self.log_channel.send(embed=embed_uncage)

    # @command(name="profanity", aliases=["curse", "swears"])
    # @has_permissions(manage_guild=True)
    # async def add_profanity(self, ctx, *word):
    #     with open("./data/profanity.txt", "a", encoding="utf-8") as f:
    #         f.write("".join([f"{w}\n" for w in word]))
    #
    #     profanity.load_censor_words_from_file("./data/profanity.txt")
    #     await ctx.send("Word Added")
    #
    # @command(name="delprofanity", aliases=["delcurse", "delswears"])
    # @has_permissions(manage_guild=True)
    # async def remove_profanity(self, ctx, *word):
    #     with open("./data/profanity.txt", "r", encoding="utf-8") as f:
    #         stored = [w.strip() for w in f.readlines()]
    #
    #     with open("./data/profanity.txt", "w", encoding="utf-8") as f:
    #         f.write("".join([f"{w}\n" for w in stored if w not in word]))
    #
    #     profanity.load_censor_words_from_file("./data/profanity.txt")
    #     await ctx.send("Removed Word")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(760492361343565824)
            self.mute_role = self.bot.guild.get_role(1004809068298391702)  # create a mute role
            self.bot.cogs_ready.ready_up("mod")

    # anti spam / auto mod
    @Cog.listener()
    async def on_message(self, message: Message):
        def _check(m):
            return (m.author == message.author
                    and len(m.mentions)
                    and (datetime.utcnow() - m.created_at).seconds < 2)  # in what time period

        if not message.author.bot:
            if len(list(filter(lambda m: _check(m), self.bot.cached_messages))) >= 15:  # @ count
                await message.channel.send("Do not spam mentions!", delete_after=10)
                # mute someone for 15 seconds after they @ someone 3 times in 1 minute (currently disabled)
                # mute length
                unmutes = await self.mute_members(message, [message.author], 1, reason="Mention Spam")

                if len(unmutes):
                    # mute length
                    await sleep(1)
                    await self.unmute_members(message.guild, [message.author])
                # await self.kick_members(message, [message.author], reason="Mention Spam") Kicks member on mentioning someone 3 times in 1 minute

            elif message.channel.id in self.no_links and search(self.url_regex, message.content):
                await message.delete()
                await message.channel.send("No links allowed here.", delete_after=10)

            elif message.channel.id in self.no_images and any([hasattr(a, "width") for a in message.attachments]):
                await message.delete()
                await message.channel.send("You can't send images here.")


def setup(bot):
    bot.add_cog(Mod(bot))
