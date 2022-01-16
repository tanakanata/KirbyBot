import os
import discord
from discord.ext import commands

TOKEN = os.environ["KIRBY_TOKEN"]


intents = discord.Intents.all()

bot = commands.Bot(command_prefix='//', intents=intents, help_command=None)

cog_list = ['Forward', 'Ban', 'Help']


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
async def shutdown(ctx):
    print("shutdown")
    await ctx.send('shutdown')
    try:
        await bot.logout()
    except:  # noqa
        print("EnvironmentError")
        bot.clear()

if __name__ == '__main__':
    for cog in cog_list:
        name = f'Cogs.{cog}'
        bot.load_extension(name)

bot.run(TOKEN)
