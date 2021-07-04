import json
import requests
import discord
from pytz import timezone
from discord.ext import commands


class Ban(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        print(__name__)

    def load_json(self):
        load_file = open('ban_list.json', 'r', encoding="utf-8_sig")
        json_data = json.load(load_file)
        load_file.close
        return json_data

    def save_json(self, json_data):
        save_file = open('ban_list.json', 'w')
        json.dump(json_data, save_file)
        save_file.close

    def get_uuid(self, mcid: str):
        url = 'https://api.mojang.com/users/profiles/minecraft/{0}'.format(
            mcid)
        res = requests.get(url)

        status_code = res.status_code
        return res, status_code

    @commands.command(name='uuid')
    async def _uuid(self, ctx: commands.context, mcid: str):
        res, status_code = self.get_uuid(mcid)
        if status_code == 204:
            await ctx.send('IDが見つかりませんでした')
            return
        elif status_code == 200:
            uuid = res.json()['id']
            await ctx.send(uuid)
        else:
            await ctx.send('サーバーエラー')

    @commands.command(name='ban')
    @commands.has_any_role(278312017775820801, 800638758394265610)
    async def _ban(self, ctx: commands.context, mcid: str, reason: str):
        json_key = mcid.lower()

        json_data = self.load_json()
        if json_key in json_data:
            await ctx.send('このIDはすでにBAN登録されています')
            return
        # ニックネームが設定されているか確認　設定されていない場合名前を指定
        if ctx.author.nick is None:
            registerer = ctx.author.name
        else:
            registerer = ctx.author.nick

        message_link = 'https://discord.com/channels/{0}/{1}/{2}'.format(
            ctx.guild.id, ctx.message.channel.id, ctx.message.id)
        created_at_utc = ctx.message.created_at
        created_at_jst = created_at_utc.astimezone(
            timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
        res, status_code = self.get_uuid(mcid)
        if status_code == 204:
            await ctx.send('IDが見つかりませんでした')
            return
        elif status_code == 200:
            minecraft_id = res.json()['name']
            uuid = res.json()['id']
        else:
            await ctx.send('サーバーエラー')

        json_data[json_key] = {
            "minecraft_id": minecraft_id,
            "uuid": uuid,
            "reason": reason,
            "registerer": registerer,
            "time": created_at_jst,
            "message_link": message_link
        }

        self.save_json(json_data)

        face_url = f'https://crafatar.com/avatars/{uuid}'

        embed = discord.Embed(
            title=minecraft_id, description=uuid, color=0xff0000)
        embed.set_thumbnail(
            url=face_url)
        embed.add_field(name="BAN理由", value=reason, inline=False)
        embed.add_field(name="BAN登録", value=registerer, inline=True)
        embed.add_field(name="日時", value=created_at_jst, inline=True)
        embed.add_field(
            name="リンク", value=f"[{message_link}]({message_link})", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='search')
    @commands.has_any_role(278312017775820801, 800638758394265610)
    async def _search(self, ctx, mcid):
        json_data = self.load_json()
        json_key = mcid.lower()

        if json_key not in json_data:
            await ctx.send('指定されたIDは見つかりませんでした')
            return

        user_data = json_data[json_key]
        minecraft_id = user_data['minecraft_id']
        uuid = user_data['uuid']
        reason = user_data['reason']
        registerer = user_data['registerer']
        time = user_data['time']
        message_link = user_data['message_link']
        face_url = f'https://crafatar.com/avatars/{uuid}'

        embed = discord.Embed(
            title=minecraft_id, description=uuid, color=0xff0000)
        embed.set_thumbnail(
            url=face_url)
        embed.add_field(name="BAN理由", value=reason, inline=False)
        embed.add_field(name="BAN登録", value=registerer, inline=True)
        embed.add_field(name="日時", value=time, inline=True)
        embed.add_field(
            name="リンク", value=f"[{message_link}]({message_link})", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='unban')
    @commands.has_any_role(278312017775820801, 800638758394265610)
    async def _unban(self, ctx, mcid):
        json_data = self.load_json()
        json_key = mcid.lower()

        if json_key not in json_data:
            await ctx.send('指定されたIDは登録されていません')
            return

        json_data.pop(mcid)

        self.save_json(json_data)
        await ctx.send('削除しました')

    @commands.command(name='old_ban')
    @commands.has_any_role(278312017775820801, 800638758394265610)
    async def _old_ban(self, ctx: commands.context, mcid: str, reason: str, registerer: str, time, message_link):
        json_key = mcid.lower()

        json_data = self.load_json()
        if json_key in json_data:
            await ctx.send('このIDはすでにBAN登録されています')
            return

        res, status_code = self.get_uuid(mcid)
        if status_code == 204:
            await ctx.send('IDが見つかりませんでした')
            return
        elif status_code == 200:
            minecraft_id = res.json()['name']
            uuid = res.json()['id']
        else:
            await ctx.send('サーバーエラー')

        json_data[json_key] = {
            "minecraft_id": minecraft_id,
            "uuid": uuid,
            "reason": reason,
            "registerer": registerer,
            "time": time,
            "message_link": message_link
        }

        self.save_json(json_data)


def setup(bot):
    bot.add_cog(Ban(bot))
