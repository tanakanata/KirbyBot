import json
import discord
from pytz import timezone
from discord.ext import commands


class Forward(commands.Cog):
    def __init__(self, bot: commands.bot) -> None:
        print(__name__)
        self.bot = bot
        self.guild_id: int = None
        self.channel_id: list = None
        self.subscriber_id: list = None
        self.admin_role_id: int = None
        self.volunteer_role_id: int = None
        self.read_json()

    def read_json(self):
        rf = open('config.json', 'r')
        json_data = json.load(rf)
        self.guild_id = json_data["guild_id"]
        self.channel_id = json_data["channel_id"]
        self.subscriber_id = json_data["Subscriber_id"]
        self.admin_role_id = json_data["admin_role_id"]
        self.volunteer_role_id = ["volunteer_role_id"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id not in self.channel_id:
            return
        created_at_utc = message.created_at
        created_at_jst = created_at_utc.astimezone(
            timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
        attachments = message.attachments
        url_list: list = []
        links: str = ''
        if len(attachments) != 0:
            for att in attachments:
                url_list.append(att.url)
            links = '\n'.join(url_list)
        else:
            for link in attachments:
                att = link + '\n'

        content = message.content
        if not content == '':
            content = content + '\n'

        msg = '{0} : {1}\n{2}{3}'.format(
            created_at_jst, message.author.nick, content, links)

        for id in self.subscriber_id:
            user = self.bot.get_user(id)
            try:
                await user.send(msg)
            except discord.Forbidden:
                print('ブロックされています')

    @commands.command()
    async def subscribe(self, ctx: commands.context, user_id: int):
        self.subscriber_id.append(user_id)


def setup(bot):
    bot.add_cog(Forward(bot))
