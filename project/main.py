import discord
import asyncio

from discord.ext import commands
import random

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("$"),
    description=description,
    intents=intents
)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def ping(ctx):
    await ctx.send("pong")

async def main():
    async with bot:
        await bot.add_cog()
        await bot.start('MTEzNzMyNzY0MzMzMTY3MDAyNw.G9JtS0.yLGC4qe6hpwnb1y9Z69dh19dfUYnTCVyCt0Ft0')


asyncio.run(main())