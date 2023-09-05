from discord.ext import commands
import discord


class Reporting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def report(self, ctx, member: discord.Member, *, reason=None):
        if reason is None:
            await ctx.send("You need to specify a reason!")
            return

        # get the channel by its ID - replace 'channel_id' with your channel's ID
        channel_id = 1137435495148834846
        report_channel = self.bot.get_channel(channel_id)

        embed = discord.Embed(title=f"Report for {member.name}",
                              description=f"Reported by: {ctx.message.author.mention}\nReason: {reason}",
                              color=discord.Color.red())

        await report_channel.send(embed=embed)
        await ctx.send(f"{member} has been reported successfully!")


async def setup(bot):
    await bot.add_cog(Reporting(bot))
