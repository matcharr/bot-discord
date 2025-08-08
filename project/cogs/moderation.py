import asyncio
import json
from typing import re

from discord.ext import commands
import discord


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            with open('warnings.json', 'r') as file:
                self.warnings = json.load(file)
        except FileNotFoundError:
            self.warnings = {}
            with open('warnings.json', 'w') as file:
                json.dump(self.warnings, file)

    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        if str(member.id) not in self.warnings:
            self.warnings[str(member.id)] = []
        self.warnings[str(member.id)].append(reason)

        with open('warnings.json', 'w') as file:
            json.dump(self.warnings, file)
        await ctx.send(f'{member} has been warned for {reason}')
        await self.log(ctx.guild, "Warning", member, reason)

    @commands.command(name='warnings')
    @commands.has_permissions(manage_messages=True)
    async def list_warnings(self, ctx, member: discord.Member):
        user_warnings = self.warnings.get(str(member.id), [])
        await ctx.send(f'Warnings for {member}: {", ".join(user_warnings)}')

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'{member} has been kicked for {reason}')

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'{member} has been banned for {reason}')

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminatore = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminatore):
                await ctx.guild.unban(user)
                await ctx.send(f'{user} has been unbanned.')
                return

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")

            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)

        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f'{member} has been muted for {reason}')

    @commands.command(name='tempban')
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, member: discord.Member, duration: str, *, reason=None):
        seconds = self.parse_time(duration)
        if seconds is None:
            await ctx.send('Invalid time format. Use `m` for minutes, `h` for hours, or `d` for days.')
            return

        await member.ban(reason=reason)
        await ctx.send(f'{member} has been banned for {duration} for {reason}')
        await asyncio.sleep(seconds)
        await ctx.guild.unban(member)
        await ctx.send(f'{member} has been unbanned.')
        await self.log(ctx.guild, f"Temporary ban for {duration}", member, reason)

    @commands.command(name='tempmute')
    @commands.has_permissions(manage_roles=True)
    async def tempmute(self, ctx, member: discord.Member, duration: str, *, reason=None):
        seconds = self.parse_time(duration)
        if seconds is None:
            await ctx.send('Invalid time format. Use `m` for minutes, `h` for hours, or `d` for days.')
            return

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            # If there is no Muted role, create one
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)

        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f'{member} has been muted for {duration} for {reason}')
        await asyncio.sleep(seconds)
        await member.remove_roles(muted_role)
        await ctx.send(f'{member} has been unmuted.')
        await self.log(ctx.guild, f"Temporary mute for {duration}", member, reason)

    @commands.command(name='purge')
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int, member: discord.Member = None, *, content_filter: str = None):
        if amount < 1:
            await ctx.send('Please specify a positive amount of messages to delete.')
            return

        def check_messages(msg):
            if member and msg.author != member:
                return False
            if content_filter and content_filter not in msg.content:
                return False
            return True

        deleted = await ctx.channel.purge(limit=amount + 1, check=check_messages)
        await ctx.send(f'Deleted {len(deleted) - 1} emssage(s)', delete_after=5)

    @staticmethod
    def parse_time(time: str):
        match = re.match(r"(\d+)([mhd])", time)
        if match:
            amount, unit = match.groups()
            amount = int(amount)
            if unit == 'm':
                return amount * 60
            elif unit == 'h':
                return amount * 60 * 60
            elif unit == 'd':
                return amount * 60 * 60 * 24
            return None

    @staticmethod
    async def log(guild, action, user, reason):
        logging_channel = discord.utils.get(guild.text_channels, name="logs")
        if logging_channel:
            await logging_channel.send(f'{action} on {user} for reason: {reason}')
        else:
            print(f'Logging channel not found in {guild.name}')


async def setup(bot):
    await bot.add_cog(Moderation(bot))
