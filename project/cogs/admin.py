"""Admin commands for bot management."""

import sys
from datetime import datetime

import discord
import psutil
from config import config
from discord.ext import commands
from utils.backup import backup_manager
from utils.health import health_checker


class Admin(commands.Cog):
    """Administrative commands for bot management."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="health")
    @commands.has_permissions(administrator=True)
    async def health_check(self, ctx):
        """Display bot health status."""
        if health_checker:
            embed = await health_checker.create_health_embed()

            # Add system info
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()

            embed.add_field(
                name="System Resources",
                value=f"Memory: {memory_mb:.1f}MB\nCPU: {cpu_percent:.1f}%",
                inline=True,
            )

            embed.add_field(
                name="Python Version",
                value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                inline=True,
            )

            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Health checker not initialized.")

    @commands.command(name="backup")
    @commands.has_permissions(administrator=True)
    async def create_backup(self, ctx, filename: str = "warnings.json"):
        """Create a backup of bot data."""
        backup_path = backup_manager.create_backup(filename)

        if backup_path:
            await ctx.send(f"✅ Backup created: `{backup_path.name}`")
        else:
            await ctx.send(f"❌ Failed to create backup of `{filename}`")

    @commands.command(name="listbackups")
    @commands.has_permissions(administrator=True)
    async def list_backups(self, ctx):
        """List available backups."""
        backups = backup_manager.list_backups()

        if not backups:
            await ctx.send("No backups found.")
            return

        embed = discord.Embed(title="📁 Available Backups", color=discord.Color.blue())

        backup_list = []
        for backup in sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True)[
            :10
        ]:
            size_kb = backup.stat().st_size / 1024
            modified = datetime.fromtimestamp(backup.stat().st_mtime)
            backup_list.append(
                f"`{backup.name}` ({size_kb:.1f}KB, {modified.strftime('%Y-%m-%d %H:%M')})"
            )

        embed.description = "\n".join(backup_list)
        await ctx.send(embed=embed)

    @commands.command(name="config")
    @commands.has_permissions(administrator=True)
    async def show_config(self, ctx):
        """Display current bot configuration."""
        embed = discord.Embed(title="⚙️ Bot Configuration", color=discord.Color.blue())

        embed.add_field(
            name="General",
            value=f"Prefix: `{config.command_prefix}`\n"
            f"Case Insensitive: {config.case_insensitive}",
            inline=True,
        )

        embed.add_field(
            name="Anti-Raid",
            value=f"Spam Threshold: {config.spam_threshold}\n"
            f"Kick Threshold: {config.kick_threshold}\n"
            f"Cooldown: {config.cooldown_seconds}s",
            inline=True,
        )

        embed.add_field(
            name="Moderation",
            value=f"Max Warnings: {config.max_warnings_before_action}\n"
            f"Audit Logging: {config.enable_audit_logging}",
            inline=True,
        )

        embed.add_field(
            name="Logging", value=f"Log Level: {config.log_level}", inline=True
        )

        await ctx.send(embed=embed)

    @commands.command(name="reload")
    @commands.has_permissions(administrator=True)
    async def reload_cog(self, ctx, cog_name: str):
        """Reload a specific cog."""
        try:
            await self.bot.reload_extension(f"cogs.{cog_name}")
            await ctx.send(f"✅ Reloaded cog: `{cog_name}`")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"❌ Cog `{cog_name}` is not loaded.")
        except commands.ExtensionNotFound:
            await ctx.send(f"❌ Cog `{cog_name}` not found.")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload `{cog_name}`: {e}")


async def setup(bot):
    await bot.add_cog(Admin(bot))
