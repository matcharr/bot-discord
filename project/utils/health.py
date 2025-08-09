"""Health check utilities for the bot."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import discord

logger = logging.getLogger(__name__)


class HealthChecker:
    """Monitors bot health and performance."""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        self.command_count = 0
        self.error_count = 0
        self.last_errors: List[str] = []
        self.max_error_history = 10

    def record_command(self):
        """Record a command execution."""
        self.command_count += 1

    def record_error(self, error: str):
        """Record an error."""
        self.error_count += 1
        self.last_errors.append(f"{datetime.utcnow().isoformat()}: {error}")

        # Keep only recent errors
        if len(self.last_errors) > self.max_error_history:
            self.last_errors.pop(0)

    def get_uptime(self) -> timedelta:
        """Get bot uptime."""
        return datetime.utcnow() - self.start_time

    def get_health_status(self) -> Dict:
        """Get comprehensive health status."""
        uptime = self.get_uptime()

        return {
            "status": "healthy" if self.error_count < 10 else "degraded",
            "uptime": str(uptime),
            "uptime_seconds": uptime.total_seconds(),
            "commands_executed": self.command_count,
            "errors": self.error_count,
            "guilds": len(self.bot.guilds),
            "users": sum(guild.member_count for guild in self.bot.guilds),
            "latency": round(self.bot.latency * 1000, 2),  # ms
            "last_errors": self.last_errors[-5:],  # Last 5 errors
        }

    async def create_health_embed(self) -> discord.Embed:
        """Create a health status embed."""
        status = self.get_health_status()

        color = (
            discord.Color.green()
            if status["status"] == "healthy"
            else discord.Color.orange()
        )

        embed = discord.Embed(
            title="🏥 Bot Health Status", color=color, timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="Status",
            value=f"{'✅' if status['status'] == 'healthy' else '⚠️'} {status['status'].title()}",
            inline=True,
        )

        embed.add_field(name="Uptime", value=status["uptime"], inline=True)

        embed.add_field(name="Latency", value=f"{status['latency']}ms", inline=True)

        embed.add_field(name="Servers", value=str(status["guilds"]), inline=True)

        embed.add_field(name="Users", value=str(status["users"]), inline=True)

        embed.add_field(
            name="Commands", value=str(status["commands_executed"]), inline=True
        )

        if status["errors"] > 0:
            embed.add_field(name="Errors", value=str(status["errors"]), inline=True)

            if status["last_errors"]:
                embed.add_field(
                    name="Recent Errors",
                    value="\n".join(status["last_errors"][-3:]),
                    inline=False,
                )

        return embed


# Global health checker instance (will be initialized in main.py)
health_checker: Optional[HealthChecker] = None
