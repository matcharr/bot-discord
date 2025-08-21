from discord.ext import commands


class WelcomeGoodBye(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Code to send a welcome message when a new member joins
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(
                f"Welcome to our server, {member.mention}! We hope you enjoy your stay.",
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Code to send a goodbye message wen a member leaves
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(
                f"{member.name} has left the server. We hope to see you again.",
            )


async def setup(bot):
    await bot.add_cog(WelcomeGoodBye(bot))
