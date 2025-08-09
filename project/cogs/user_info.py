import discord
from discord.ext import commands


class UserInfo(commands.Cog):
    @commands.command(name="user_info", aliases=["user", "uinfo"])
    async def user_info(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        roles = [role.name for role in member.roles[1:]]  # Exclude the @everyone role
        roles_str = ", ".join(roles) if roles else "None"

        embed = discord.Embed(
            title=f"User Information for {member}", color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Username", value=member.name, inline=False)
        embed.add_field(name="Nickname", value=member.nick or "None", inline=False)
        embed.add_field(
            name="Joined Server",
            value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            inline=False,
        )
        embed.add_field(name="Roles", value=roles_str, inline=False)

        await ctx.send(embed=embed)

    @user_info.error
    async def user_info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("I couldn't find that member. Please try again.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(UserInfo(bot))
