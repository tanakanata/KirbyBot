from os import name
from discord.ext import commands
from discord.ext.commands.core import command


class Help(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        print(__name__)

    @commands.command()
    async def help(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Help(bot))
