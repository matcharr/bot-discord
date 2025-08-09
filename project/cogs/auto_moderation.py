import discord
from discord.ext import commands


class AutoModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_counter = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Filter for banned words
        banned_words = ["badword1", "badword2"]
        if any(word in message.content for word in banned_words):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, that word is no allowed.", delete_after=5
            )
            return

        # Prevent spam (3 messages in 5 seconds)
        author_id = message.author.id
        self.spam_counter[author_id] = self.spam_counter.get(author_id, 0) + 1

        if self.spam_counter[author_id] >= 3:
            muted_role = discord.utils.get(message.guild.roles, name="Muted")
            if not muted_role:
                muted_role = await message.guild.create_role(name="Muted")
                for channel in message.guild.channels:
                    await channel.set_permissions(
                        muted_role, speak=False, send_messages=False
                    )

            await message.author.add_roles(muted_role)
            await message.channel.send(
                f"{message.author.mention} has been muted for spamming.", delete_after=5
            )
        await self.bot.loop.call_later(5, self.reset_spam_counter, author_id)

    def reset_spam_counter(self, author_id):
        self.spam_counter[author_id] = 0


async def setup(bot):
    await bot.add_cog(AutoModeration(bot))
