import logging

from discord.ext import commands

logger = logging.getLogger(__name__)


class InviteManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.invites[guild.id] = await guild.invites()

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        # Notify in console or log file
        logger.info(f"Invite created: {invite.url}")

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        # Notify in console or log file
        logger.info(f"Invite deleted: {invite.url}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        try:
            invites_before_join = self.invites[member.guild.id]
            invites_after_join = await member.guild.invites()
            self.invites[member.guild.id] = invites_after_join
            used_invite = next(
                invite
                for invite in invites_before_join
                if invite not in invites_after_join
            )

            # Here, you can store `used_invite` data somewhere or do something with it
            logger.info(f"{member.name} used invite {used_invite.url}")

        except Exception:
            logger.exception("Error tracking invite usage")


async def setup(bot):
    await bot.add_cog(InviteManagement(bot))
