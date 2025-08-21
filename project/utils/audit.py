"""Audit logging for security events."""

import contextlib
import logging
from datetime import datetime

import discord


audit_logger = logging.getLogger("audit")


async def log_moderation_action(
    action: str,
    moderator: discord.Member,
    target: discord.Member,
    reason: str | None = None,
    guild: discord.Guild | None = None,
):
    """Log moderation actions for audit trail."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "moderator": f"{moderator} ({moderator.id})",
        "target": f"{target} ({target.id})",
        "reason": reason or "No reason provided",
        "guild": guild.name if guild else "Unknown",
    }

    audit_logger.info(f"MODERATION: {log_entry}")

    # Optional: Send to audit channel
    if guild:
        audit_channel = discord.utils.get(guild.text_channels, name="audit-logs")
        if audit_channel:
            embed = discord.Embed(
                title=f"🔨 Moderation Action: {action}",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Moderator", value=moderator.mention, inline=True)
            embed.add_field(name="Target", value=target.mention, inline=True)
            embed.add_field(name="Reason", value=reason or "No reason", inline=False)

            with contextlib.suppress(discord.Forbidden):
                await audit_channel.send(embed=embed)
