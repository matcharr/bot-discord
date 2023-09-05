from discord.ext import commands
from collections import defaultdict
import discord
import asyncio


class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_count = defaultdict(int)
        self.spam_users = set()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Do not count messages from bots or admins
        if message.author.bot or message.author.guild_permissions.administrator:
            return

        self.spam_count[message.author] += 1
        if self.spam_count[message.author] == 5:  # If user has sent 5 messages...
            self.spam_users.add(message.author)

        if message.author in self.spam_users:
            if self.spam_count[message.author] >= 10:  # If user has sent 10 or more messages...
                await message.author.kick(reason="Spam detected")  # Kick the user
                del self.spam_count[message.author]
                self.spam_users.remove(message.author)

        await asyncio.sleep(10)  # After 10 seconds...
        self.spam_count[message.author] -= 1  # Remove 1 from the count
        if self.spam_count[message.author] == 0:
            self.spam_users.discard(message.author)  # If count is 0, remove user from spam_users


async def setup(bot):
    await bot.add_cog(AntiRaid(bot))
