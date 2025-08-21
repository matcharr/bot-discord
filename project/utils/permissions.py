"""Permission validation utilities."""

import discord
from discord.ext import commands


def check_bot_permissions(required_perms: list[str]):
    """Decorator to check if bot has required permissions."""

    async def predicate(ctx):
        bot_perms = ctx.channel.permissions_for(ctx.guild.me)
        missing_perms = [
            perm for perm in required_perms if not getattr(bot_perms, perm, False)
        ]

        if missing_perms:
            await ctx.send(f"❌ I'm missing permissions: {', '.join(missing_perms)}")
            return False
        return True

    return commands.check(predicate)


async def validate_hierarchy(ctx, target: discord.Member) -> bool:
    """Check if bot can act on target member (role hierarchy)."""
    if target == ctx.guild.owner:
        await ctx.send("❌ Cannot act on server owner.")
        return False

    if target.top_role >= ctx.guild.me.top_role:
        await ctx.send("❌ Target has higher or equal role than me.")
        return False

    if target.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("❌ Target has higher or equal role than you.")
        return False

    return True
