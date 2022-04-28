from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        print(__name__)

    @commands.command(ailiases=['Help'])
    async def help(self, ctx):
        msg = '!uuid <PlayerID> : UUIDを取得します \n !ban <PlayerID> <理由> : BAN情報をBOTに登録します \n !unban <PlayerID> : BAN情報をBOTから削除します \n !search <PlayerID> : BAN情報を検索します'

        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Help(bot))
