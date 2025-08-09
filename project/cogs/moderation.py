import asyncio
import json
import logging

import re
from pathlib import Path
from typing import Dict, List, Optional

import discord
from config import config
from discord.ext import commands
from utils.audit import log_moderation_action
from utils.permissions import validate_hierarchy

logger = logging.getLogger(__name__)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.warnings_file = self.data_dir / "warnings.json"
        self.warnings: Dict[str, List[str]] = self._load_warnings()

    def _load_warnings(self) -> Dict[str, List[str]]:
        """Load warnings from JSON file with error handling."""
        try:
            if self.warnings_file.exists():
                with open(self.warnings_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    # Validate data structure
                    if isinstance(data, dict):
                        return {k: v for k, v in data.items() if isinstance(v, list)}
                    return {}
            return {}
        except (json.JSONDecodeError, PermissionError) as e:
            logger.error(f"Error loading warnings: {e}")
            return {}

    def _save_warnings(self) -> bool:
        """Save warnings to JSON file with error handling."""
        try:
            with open(self.warnings_file, "w", encoding="utf-8") as file:
                json.dump(self.warnings, file, indent=2, ensure_ascii=False)
            return True
        except (PermissionError, OSError) as e:
            logger.error(f"Error saving warnings: {e}")
            return False

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: Optional[str] = None):
        # Validation
        if not await validate_hierarchy(ctx, member):
            return

        if not reason:
            await ctx.send("❌ Please provide a reason for the warning.")
            return

        if len(reason) > 500:
            await ctx.send("❌ Warning reason must be less than 500 characters.")
            return

        # Add warning
        user_id = str(member.id)
        if user_id not in self.warnings:
            self.warnings[user_id] = []
        self.warnings[user_id].append(reason)

        # Save to file
        if not self._save_warnings():
            await ctx.send("⚠️ Warning added but failed to save to file.")

        # Check if user has reached warning limit
        warning_count = len(self.warnings[user_id])
        max_warnings = config.max_warnings_before_action

        embed = discord.Embed(
            title="⚠️ User Warned",
            color=discord.Color.orange(),
            description=f"{member.mention} has been warned.",
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(
            name="Warning Count", value=f"{warning_count}/{max_warnings}", inline=True
        )
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)

        if warning_count >= max_warnings:
            embed.add_field(
                name="⚠️ Action Required",
                value=f"User has reached {max_warnings} warnings!",
                inline=False,
            )

        await ctx.send(embed=embed)
        await self.log(ctx.guild, "Warning", member, reason)
        await log_moderation_action("WARN", ctx.author, member, reason, ctx.guild)

    @commands.command(name="warnings")
    @commands.has_permissions(manage_messages=True)
    async def list_warnings(self, ctx, member: discord.Member):
        user_warnings = self.warnings.get(str(member.id), [])

        embed = discord.Embed(
            title=f"📋 Warnings for {member.display_name}", color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        if not user_warnings:
            embed.description = "No warnings found."
        else:
            for i, warning in enumerate(user_warnings, 1):
                embed.add_field(
                    name=f"Warning #{i}",
                    value=warning or "No reason provided",
                    inline=False,
                )

        embed.set_footer(text=f"Total warnings: {len(user_warnings)}")
        await ctx.send(embed=embed)

    @commands.command(name="clearwarnings")
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        """Clear all warnings for a user."""
        user_id = str(member.id)
        if user_id in self.warnings:
            warning_count = len(self.warnings[user_id])
            del self.warnings[user_id]
            self._save_warnings()

            await ctx.send(
                f"✅ Cleared {warning_count} warning(s) for {member.mention}"
            )
            await log_moderation_action(
                "CLEAR_WARNINGS",
                ctx.author,
                member,
                f"Cleared {warning_count} warnings",
                ctx.guild,
            )
        else:
            await ctx.send(f"ℹ️ {member.mention} has no warnings to clear.")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: Optional[str] = None):
        if not await validate_hierarchy(ctx, member):
            return

        try:
            await member.kick(reason=reason)

            embed = discord.Embed(
                title="👢 User Kicked",
                color=discord.Color.red(),
                description=f"{member.mention} has been kicked from the server.",
            )
            embed.add_field(
                name="Reason", value=reason or "No reason provided", inline=False
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)

            await ctx.send(embed=embed)
            await log_moderation_action("KICK", ctx.author, member, reason, ctx.guild)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this user.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to kick user: {e}")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"{member} has been banned for {reason}")

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminatore = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminatore):
                await ctx.guild.unban(user)
                await ctx.send(f"{user} has been unbanned.")
                return

    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")

            for channel in ctx.guild.channels:
                await channel.set_permissions(
                    muted_role, speak=False, send_messages=False
                )

        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f"{member} has been muted for {reason}")

    @commands.command(name="tempban")
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, member: discord.Member, duration: str, *, reason=None):
        seconds = self.parse_time(duration)
        if seconds is None:
            await ctx.send(
                "Invalid time format. Use `m` for minutes, `h` for hours, or `d` for days."
            )
            return

        await member.ban(reason=reason)
        await ctx.send(f"{member} has been banned for {duration} for {reason}")
        await asyncio.sleep(seconds)
        await ctx.guild.unban(member)
        await ctx.send(f"{member} has been unbanned.")
        await self.log(ctx.guild, f"Temporary ban for {duration}", member, reason)

    @commands.command(name="tempmute")
    @commands.has_permissions(manage_roles=True)
    async def tempmute(
        self, ctx, member: discord.Member, duration: str, *, reason=None
    ):
        seconds = self.parse_time(duration)
        if seconds is None:
            await ctx.send(
                "Invalid time format. Use `m` for minutes, `h` for hours, or `d` for days."
            )
            return

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            # If there is no Muted role, create one
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(
                    muted_role, speak=False, send_messages=False
                )

        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f"{member} has been muted for {duration} for {reason}")
        await asyncio.sleep(seconds)
        await member.remove_roles(muted_role)
        await ctx.send(f"{member} has been unmuted.")
        await self.log(ctx.guild, f"Temporary mute for {duration}", member, reason)

    @commands.command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def purge(
        self,
        ctx,
        amount: int,
        member: discord.Member = None,
        *,
        content_filter: str = None,
    ):
        if amount < 1:
            await ctx.send("Please specify a positive amount of messages to delete.")
            return

        def check_messages(msg):
            if member and msg.author != member:
                return False
            if content_filter and content_filter not in msg.content:
                return False
            return True

        deleted = await ctx.channel.purge(limit=amount + 1, check=check_messages)
        await ctx.send(f"Deleted {len(deleted) - 1} emssage(s)", delete_after=5)

    @staticmethod
    def parse_time(time: str) -> Optional[int]:
        """Parse time string into seconds with validation."""
        if not time or not isinstance(time, str):
            return None

        match = re.match(r"^(\d+)([mhd])$", time.lower())
        if not match:
            return None

        amount, unit = match.groups()
        try:
            amount = int(amount)
        except ValueError:
            return None

        # Validation: reasonable limits
        if amount <= 0:
            return None

        if unit == "m":
            if amount > 10080:  # Max 1 week in minutes
                return None
            return amount * 60
        elif unit == "h":
            if amount > 168:  # Max 1 week in hours
                return None
            return amount * 3600
        elif unit == "d":
            if amount > 30:  # Max 30 days
                return None
            return amount * 86400

        return None

    @staticmethod
    async def log(guild, action, user, reason):
        """Enhanced logging with embeds."""
        logging_channel = discord.utils.get(guild.text_channels, name="logs")
        if logging_channel:
            embed = discord.Embed(
                title=f"📝 Moderation Log: {action}",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow(),
            )
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
            embed.add_field(name="Action", value=action, inline=True)
            embed.add_field(
                name="Reason", value=reason or "No reason provided", inline=False
            )

            try:
                await logging_channel.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"No permission to send to logs channel in {guild.name}")
        else:
            logger.warning(f"Logging channel not found in {guild.name}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
