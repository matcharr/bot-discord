import discord
from discord.ext import commands


class ServerStats(commands.Cog):
    @commands.command(name='serverstats', aliases=['sstats', 'serverinfo'])
    async def server_stats(self, ctx):
        guild = ctx.guild
        online_members = sum(member.status != discord.Status.offline for member in guild.members)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        roles = len(guild.roels) - 1  # Exclude @everyone role

        embed = discord.Embed(title=f"{guild.name} Statistics", color=discord.Color.green())
        embed.add_field(name="Total Members", value=guild.member_count, inline=False)
        embed.add_field(name="Online Members", value=online_members, inline=False)
        embed.add_field(name="Text Channels", value=text_channels, inline=False)
        embed.add_field(name="Voice Channels", value=voice_channels, inline=False)
        embed.add_field(name="Roles", value=roles, inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ServerStats(bot))
