import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Reporting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.user)  # 1 report per 5 minutes
    async def report(self, ctx, member: discord.Member, *, reason=None):
        if reason is None:
            await ctx.send("You need to specify a reason!")
            return

        # Validate reason length and content
        if len(reason) < 10:
            await ctx.send("❌ Reason must be at least 10 characters long.")
            return

        if len(reason) > 500:
            await ctx.send("❌ Reason must be less than 500 characters.")
            return

        # Prevent self-reporting
        if member == ctx.author:
            await ctx.send("❌ You cannot report yourself.")
            return

        # get the channel by its ID from environment variable
        channel_id = int(os.getenv("REPORT_CHANNEL_ID", "0"))
        report_channel = self.bot.get_channel(channel_id)

        if channel_id == 0:
            await ctx.send(
                "❌ Report channel not configured. "
                "Please set REPORT_CHANNEL_ID in .env file.",
            )
            return

        if not report_channel:
            await ctx.send(
                "❌ Report channel not found. Please contact an administrator.",
            )
            return

        embed = discord.Embed(
            title=f"Report for {member.name}",
            description=f"Reported by: {ctx.message.author.mention}\nReason: {reason}",
            color=discord.Color.red(),
        )

        try:
            await report_channel.send(embed=embed)
            await ctx.send(f"✅ {member} has been reported successfully!")
        except discord.Forbidden:
            await ctx.send(
                "❌ I don't have permission to send messages to the report channel.",
            )
        except Exception:
            await ctx.send("❌ Failed to send report. Please try again later.")
            logger.exception("Report error")


async def setup(bot):
    await bot.add_cog(Reporting(bot))
