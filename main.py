import os
import discord
from discord.ext import commands

TOKEN = os.environ(['KIRBY_TOKEN'])

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

cog_list = ['Forward', 'MCUUID']


@bot.event
async def on_ready():
    print('ready')


@bot.command()
async def reload(ctx):
    for cog in cog_list:
        name = f'Cogs.{cog}'
        bot.reload_extension(name)
    await ctx.send('Reload complete.')


@bot.command()
# @commands.has_role()
async def shutdown(ctx):
    pass
