import discord
from discord.ext import commands


class LoggingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        log_channel = discord.utils.get(message.guild.text_channels, name="logs")

        if log_channel:
            embed = discord.Embed(title="Message Deleted", color=discord.Color.red())
            embed.add_field(name="Author", value=message.author.mention, inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=False)
            embed.add_field(name="Content", value=message.content or "None", inline=False)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = discord.utils.get(member.guild.text_channels, name="logs")
        if log_channel:
            embed = discord.Embed(title="Member Joined", color=discord.Color.green())
            embed.add_field(name="Member", value=member.mention, inline=False)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_channel = discord.utils.get(member.guild.text_channels, name="logs")
        if log_channel:
            embed = discord.Embed(title="Member Left", color=discord.Color.orange())
            embed.add_field(name="Member", value=member.mention, inline=False)
            await log_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LoggingSystem(bot))
