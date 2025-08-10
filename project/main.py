#!/usr/bin/env python3
"""
Discord Moderation Bot
A comprehensive Discord bot with moderation tools and anti-raid protection.
"""

import asyncio

import discord
import utils.health as health_module
from config import get_config
from discord.ext import commands
from utils.health import HealthChecker
from utils.logger import setup_logger

# Setup logging
logger = setup_logger()

# Initialize health checker
health_checker = None

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=get_config().command_prefix,
    case_insensitive=get_config().case_insensitive,
    intents=intents,
    help_command=None,  # We'll create a custom one
)


@bot.event
async def on_ready():
    """Bot startup event."""
    global health_checker

    logger.info(f"{bot.user} has connected to Discord!")
    logger.info(f"Bot is in {len(bot.guilds)} guilds")

    # Initialize health checker
    health_checker = HealthChecker(bot)
    health_module.health_checker = health_checker

    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="for rule violations"
        )
    )


@bot.event
async def on_command(ctx):
    """Track command usage."""
    if health_checker:
        health_checker.record_command()


@bot.event
async def on_command_error(ctx, error):
    """Global error handler."""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have the required permissions for this command.")
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ Command on cooldown. Try again in {error.retry_after:.1f}s")
        return

    # Log unexpected errors
    error_msg = f"Unexpected error in command {ctx.command}: {error}"
    logger.error(error_msg)

    if health_checker:
        health_checker.record_error(error_msg)

    await ctx.send("❌ An unexpected error occurred. Please try again later.")


async def load_cogs():
    """Load all bot cogs."""
    cogs = [
        "cogs.anti_raid",
        "cogs.moderation",
        "cogs.logging_system",
        "cogs.role_management",
        "cogs.invite_management",
        "cogs.reporting",
        "cogs.admin",
    ]

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"Loaded cog: {cog}")
        except Exception as e:
            logger.error(f"Failed to load cog {cog}: {e}")
            if health_checker:
                health_checker.record_error(f"Failed to load cog {cog}: {e}")


async def main():
    """Main bot function."""
    try:
        await load_cogs()
        await bot.start(get_config().token)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
