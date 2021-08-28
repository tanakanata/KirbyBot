import json
import requests
import re
import datetime
import discord
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
        json.dump(json_data, save_file, indent=4)
        save_file.close

    def get_uuid(self, mcid: str):
        url = 'https://api.mojang.com/users/profiles/minecraft/{0}'.format(
            mcid)
        res = requests.get(url)

        status_code = res.status_code
        return res, status_code

    def get_name_history(self, uuid: str):
        url = 'https://api.mojang.com/users/profiles/{0}/name'.format(
            uuid)
        res = requests.get(url)

        status_code = res.status_code
        return res, status_code

    def get_face(self, uuid: str):
        url = f'https://crafatar.com/avatars/{uuid}'
        return url

    @commands.command(name='tempban', alliases=['Tempban', 'TempBan', 'TempBAN' 'tempBan', 'tempBAN', 'TEMPBAN'])
    @commands.guild_only()
    @commands.has_any_role(278312017775820801, 800638758394265610)
    async def _tempban(self, ctx: commands.context, term: str, mcid: str, reason: str):
        # 最新のBAN情報を読み出し
        json_data = self.load_json()
        minecraft_id_list = [i.get('minecraft_id').casefold() for i in json_data]

        # termの書式を判定
        if not re.fullmatch(r'^\d+d$', term):
            await ctx.send('期間が認識できませんでした。')
            return

        # すでにBANされているか確認
        if mcid.casefold() in minecraft_id_list:
            await ctx.send('このIDはすでにBAN登録されています')
            return

        # ニックネームが設定されているか確認　設定されていない場合名前を指定
        if ctx.author.nick is None:
            registerer: str = ctx.author.name
        else:
            registerer: str = ctx.author.nick

        # メッセージリンクを作成
        message_link = 'https://discord.com/channels/{0}/{1}/{2}'.format(
            ctx.guild.id, ctx.message.channel.id, ctx.message.id)

        # BANをした時間をJSTで作成
        created_at_jst: str = (ctx.message.created_at + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')

        # UUIDを取得
        res, status_code = self.get_uuid(mcid)
        if status_code == 204:
            await ctx.send('IDが見つかりませんでした')
            return
        elif status_code == 200:
            minecraft_id: str = res.json()['name']
            uuid = res.json()['id']
        else:
            await ctx.send('サーバーエラー')

        # JSONに保存する内容を作成
        add_data = [{
            "minecraft_id": minecraft_id,
            "uuid": uuid,
            "reason": reason,
            "temporary": True,
            "term": term,
            "registerer": registerer,
            "time": created_at_jst,
            "message_link": message_link
        }]

        # JSONに書き込み
        json_data[len(json_data):len(json_data)] = add_data
        self.save_json(json_data)

        # 埋め込みに使う顔のURLを取得
        face_url = self.get_face(uuid)

        # IDの文字装飾を無効化
        replace_id = minecraft_id.replace("_", r"\_")

        # embedを作成
        embed = discord.Embed(
            title=replace_id, description=uuid, color=0xffff00)
        embed.set_thumbnail(
            url=face_url)
        embed.add_field(name="BAN理由", value=reason, inline=False)
        embed.add_field(name="BAN登録", value=registerer, inline=True)
        embed.add_field(name="日時", value=created_at_jst, inline=True)
        embed.add_field(
            name="リンク", value=f"[{message_link}]({message_link})", inline=False)

        # メッセージを送信
        await ctx.send(embed=embed)

    @commands.command(name='ban', alliases=['Ban', 'BAN'])
    @commands.guild_only()
    @commands.has_any_role(278312017775820801, 800638758394265610)
    async def _ban(self, ctx: commands.context, arg: str, mcid: str, reason: str):
        # 最新のBAN情報を読み出し
        json_data = self.load_json()
        minecraft_id_list = [i.get('minecraft_id').casefold() for i in json_data]

        # 第一引数を判定
        if arg != '-p' and arg != '-s':
            await ctx.send('第一引数が間違っています。')
            return

        # ban_listに登録されているか確認
        if mcid.casefold() in minecraft_id_list:
            user_index = minecraft_id_list.index(mcid.casefold())
            user_data = json_data[user_index]

            # temporaryとして登録されていた場合、Permanentに変更
            if user_data['temporary']:
                user_data['temporary'] = False
                json_data[user_index] = user_data
                self.save_json(json_data)
                await ctx.send('永久BANに変更しました。')
                return
            else:
                await ctx.send('すでにBAN登録されています。')
                return

        # ニックネームが設定されているか確認　設定されていない場合名前を指定
        if ctx.author.nick is None:
            registerer: str = ctx.author.name
        else:
            registerer: str = ctx.author.nick

        # メッセージリンクを作成
        message_link = 'https://discord.com/channels/{0}/{1}/{2}'.format(
            ctx.guild.id, ctx.message.channel.id, ctx.message.id)

        # BANをした時間をJSTで作成
        created_at_jst: str = (ctx.message.created_at + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')

        # UUIDを取得
        res, status_code = self.get_uuid(mcid)
        if status_code == 204:
            await ctx.send('IDが見つかりませんでした')
            return
        elif status_code == 200:
            minecraft_id: str = res.json()['name']
            uuid = res.json()['id']
        else:
            await ctx.send('サーバーエラー')

        # JSONに保存する内容を作成
        add_data = [{
            "minecraft_id": minecraft_id,
            "uuid": uuid,
            "reason": reason,
            "temporary": False,
            "term": "Permanent",
            "registerer": registerer,
            "time": created_at_jst,
            "message_link": message_link
        }]

        # JSONに書き込み
        json_data[len(json_data):len(json_data)] = add_data
        self.save_json(json_data)

        # 埋め込みに使う顔のURLを取得
        face_url = self.get_face(uuid)

        # IDの文字装飾を無効化
        replace_id = minecraft_id.replace("_", r"\_")

        # embedを作成
        embed = discord.Embed(
            title=replace_id, description=uuid, color=0xff0000)
        embed.set_thumbnail(
            url=face_url)
        embed.add_field(name="BAN理由", value=reason, inline=False)
        embed.add_field(name="BAN登録", value=registerer, inline=True)
        embed.add_field(name="日時", value=created_at_jst, inline=True)
        embed.add_field(
            name="リンク", value=f"[{message_link}]({message_link})", inline=False)

        # メッセージを送信
        await ctx.send(embed=embed)

    @ commands.command(name='past_ban', aliases=['ob', 'pb'])
    @ commands.guild_only()
    @ commands.has_any_role(278312017775820801, 800638758394265610)
    async def _past_ban(self, ctx: commands.context, mcid: str, reason: str, registerer: str, time, message_link):

        json_data = self.load_json()
        minecraft_id_list = [i.get('minecraft_id').casefold() for i in json_data]

        if mcid.casefold() in minecraft_id_list:
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

        add_data = [{
            "minecraft_id": minecraft_id,
            "uuid": uuid,
            "reason": reason,
            "temporary": False,
            "registerer": registerer,
            "time": time,
            "message_link": message_link
        }]

        json_data[len(json_data):len(json_data)] = add_data
        self.save_json(json_data)

        await ctx.send('登録しました')

    @ commands.command(name='unban', aliases=['Unban', 'UNBAN'])
    @ commands.guild_only()
    @ commands.has_any_role(278312017775820801, 800638758394265610)
    async def _unban(self, ctx, mcid):
        json_data = self.load_json()
        minecraft_id_list = [i.get('minecraft_id').casefold() for i in json_data]

        if mcid.casefold() not in minecraft_id_list:
            await ctx.send('指定されたIDは登録されていません')
            return

        user_index = minecraft_id_list.index(mcid.casefold())
        json_data.pop(user_index)

        self.save_json(json_data)
        await ctx.send('削除しました')

    @ commands.command(name='search', alliases=['Search', 'SEARCH', 's'])
    @ commands.guild_only()
    @ commands.has_any_role(278312017775820801, 800638758394265610)
    async def _search(self, ctx, mcid):
        json_data = self.load_json()
        minecraft_id_list = [i.get('minecraft_id').casefold() for i in json_data]

        if mcid.casefold() not in minecraft_id_list:
            await ctx.send('指定されたIDは見つかりませんでした')
            return

        user_index = minecraft_id_list.index(mcid.casefold())
        user_data = json_data[user_index]
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

    @commands.command(name='uuid', alliases=['UUID'])
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

    @_tempban.error
    async def _tempban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: /tempban <PlayerID> <期間> <理由>')

    @ _ban.error
    async def _ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: /ban <-p or -s> <PlayerID> <理由>')

    @ _unban.error
    async def _unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: /unban <PlayerID>')

    @ _search.error
    async def _search_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: /search <PlayerID>')

    @ _uuid.error
    async def _uuid_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: /uuid <PlayerID>')


def setup(bot):
    bot.add_cog(Ban(bot))
