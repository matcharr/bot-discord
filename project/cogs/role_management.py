import discord
from discord.ext import commands


class RoleManagement(commands.Cog):
    @commands.command(name='create_role')
    @commands.has_permissions(manage_roles=True)
    async def create_role(self, ctx, name, color: discord.Color = discord.Colors.default()):
        role = await ctx.guild.create_role(name=name, color=color)
        await ctx.send(f'Role "{role.name}" has been created.')

    @commands.command(name='delete_role')
    @commands.has_permissions(manage_roles=True)
    async def delete_role(self, ctx, *, role: discord.Role):
        await role.delete()
        await ctx.send(f'Role "{role.name}" has been deleted.')

    @commands.command(name='add_role')
    @commands.has_permissions(manage_roles=True)
    async def add_role(self, ctx, member: discord.Member, *, role: discord.Role):
        await member.add_roles(role)
        await ctx.send(f'{member.mention} has been given the "{role.name}" role.')

    @commands.command(name='remove_role')
    @commands.has_permissions(manage_roles=True)
    async def remove_role(self, ctx, member: discord.Member, *, role: discord.Role):
        await member.remove_roles(role)
        await ctx.send(f'{member.mention} has been removed from the "{role.name}" role.')


async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
