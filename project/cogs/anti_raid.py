import asyncio
import logging
from collections import defaultdict

import discord
from config import get_config
from discord.ext import commands
from utils.audit import log_moderation_action

logger = logging.getLogger(__name__)


class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_count: dict[discord.Member, int] = defaultdict(int)
        self.spam_users: set[discord.Member] = set()
        self.cooldown_tasks: dict[discord.Member, asyncio.Task] = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        # Skip if not in a guild or from bots/admins
        if not message.guild or message.author.bot:
            return

        if message.author.guild_permissions.administrator:
            return

        # Increment spam count
        self.spam_count[message.author] += 1

        # Flag user as potential spammer
        if self.spam_count[message.author] == get_config().spam_threshold:
            self.spam_users.add(message.author)
            logger.info(
                f"User {message.author} flagged for spam (threshold: {get_config().spam_threshold})",
            )

        # Take action if kick threshold reached
        if (
            message.author in self.spam_users
            and self.spam_count[message.author] >= get_config().kick_threshold
        ):
            try:
                await message.author.kick(reason="Automatic kick: Spam detected")

                # Log the action
                await log_moderation_action(
                    "AUTO_KICK",
                    self.bot.user,
                    message.author,
                    "Spam detection",
                    message.guild,
                )

                # Clean up tracking
                del self.spam_count[message.author]
                self.spam_users.discard(message.author)

                # Cancel cooldown task if exists
                if message.author in self.cooldown_tasks:
                    self.cooldown_tasks[message.author].cancel()
                    del self.cooldown_tasks[message.author]

                logger.info(f"Auto-kicked {message.author} for spam")

            except discord.Forbidden:
                logger.warning(f"Failed to kick {message.author}: Missing permissions")
            except discord.HTTPException:
                logger.exception(f"Failed to kick {message.author}")

        # Start or restart cooldown
        if message.author in self.cooldown_tasks:
            self.cooldown_tasks[message.author].cancel()

        self.cooldown_tasks[message.author] = asyncio.create_task(
            self._cooldown_user(message.author),
        )

    async def _cooldown_user(self, user: discord.Member):
        """Handle user cooldown and count reduction."""
        try:
            await asyncio.sleep(get_config().cooldown_seconds)

            if user in self.spam_count:
                self.spam_count[user] -= 1

                if self.spam_count[user] <= 0:
                    del self.spam_count[user]
                    self.spam_users.discard(user)

            # Clean up task reference
            if user in self.cooldown_tasks:
                del self.cooldown_tasks[user]

        except asyncio.CancelledError:
            # Task was cancelled, clean up
            if user in self.cooldown_tasks:
                del self.cooldown_tasks[user]

    @commands.command(name="antiraidstatus")
    @commands.has_permissions(manage_guild=True)
    async def antiraid_status(self, ctx):
        """Show current anti-raid status and statistics."""
        embed = discord.Embed(title="🛡️ Anti-Raid Status", color=discord.Color.blue())

        embed.add_field(
            name="Configuration",
            value=f"Spam Threshold: {get_config().spam_threshold}\n"
            f"Kick Threshold: {get_config().kick_threshold}\n"
            f"Cooldown: {get_config().cooldown_seconds}s",
            inline=True,
        )

        embed.add_field(
            name="Current Activity",
            value=f"Tracked Users: {len(self.spam_count)}\n"
            f"Flagged Users: {len(self.spam_users)}\n"
            f"Active Cooldowns: {len(self.cooldown_tasks)}",
            inline=True,
        )

        if self.spam_users:
            flagged_users = [
                f"{user.mention} ({self.spam_count[user]})"
                for user in list(self.spam_users)[:5]
            ]  # Show max 5
            embed.add_field(
                name="Flagged Users (Top 5)",
                value="\n".join(flagged_users),
                inline=False,
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AntiRaid(bot))
