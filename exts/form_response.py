import asyncio
import importlib
import os
import typing

import aiohttp.web as web
import attrs
import interactions as ipy
import orjson

import common.utils as utils


class ItemData(typing.TypedDict):
    id: int
    question: str
    answer: str


@attrs.define()
class FormData:
    id: str
    url: str
    items: list[ItemData]


class FormResponse(ipy.Extension):
    def __init__(self, bot):
        self.bot: utils.MPBotBase = bot
        self.staff_chat: ipy.GuildText = None  # type: ignore
        self.runner: web.AppRunner = None  # type: ignore
        self.task = asyncio.create_task(self.start_server())

    def drop(self) -> None:
        asyncio.create_task(self.runner.cleanup())
        return super().drop()

    async def start_server(self):
        await self.bot.fully_ready.wait()
        self.staff_chat = await self.bot.fetch_channel(1128874166699962368)  # type: ignore

        app = web.Application()
        app.add_routes([web.post("/mp-form-response", self.form_response)])
        app.add_routes([web.post("/mp-art-form-response", self.art_form_response)])
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, port=8080)
        await site.start()

    async def form_response(
        self,
        request: web.Request,
    ):
        try:
            resp_json = await request.json(loads=orjson.loads)
        except orjson.JSONDecodeError:
            return web.Response(status=400)

        if not resp_json.get("kinda_secret"):
            return web.Response(status=404)

        if resp_json["kinda_secret"] != os.environ["KINDA_FORMS_SECRET"]:
            return web.Response(status=404)

        asyncio.create_task(self.actual_form_response(resp_json))
        return web.Response(status=200)

    async def actual_form_response(self, resp_json: dict[str, typing.Any]):
        resp_json.pop("kinda_secret")
        form_data = FormData(**resp_json)

        if await self.bot.redis.get(f"mp-form:{form_data.id}"):
            return

        user_question = next(i for i in form_data.items if i["id"] == 1532336789)
        docs_question = next(i for i in form_data.items if i["id"] == 387664031)

        username = user_question["answer"]

        username_to_search = username
        hash_split = username.split("#")
        discrim = "0"

        if len(hash_split) == 2 and hash_split[1].isdigit() and len(hash_split[1]) == 4:
            username_to_search = hash_split[0]
            discrim = hash_split[1]

        if possible_member := next(
            (
                m
                for m in self.bot.guild.members
                if m.username == username_to_search and m.discriminator == discrim
            ),
            None,
        ):
            username = possible_member.mention

        embed = ipy.Embed(
            title="New Form Response",
            color=self.bot.color,
            timestamp=ipy.Timestamp.utcnow(),
        )
        embed.add_field("Submitted User", username, inline=True)
        embed.add_field(
            "Submitted Doc", f"[Link]({docs_question['answer']})", inline=True
        )
        embed.add_field("Submitted Form", f"[Link]({form_data.url})", inline=True)

        await self.staff_chat.send(embeds=embed)
        await self.bot.redis.set(f"mp-form:{form_data.id}", "1")

    async def art_form_response(
        self,
        request: web.Request,
    ):
        try:
            resp_json = await request.json(loads=orjson.loads)
        except orjson.JSONDecodeError:
            return web.Response(status=400)

        if not resp_json.get("kinda_secret"):
            return web.Response(status=404)

        if resp_json["kinda_secret"] != os.environ["KINDA_FORMS_SECRET"]:
            return web.Response(status=404)

        asyncio.create_task(self.actual_art_response(resp_json))
        return web.Response(status=200)

    async def actual_art_response(self, resp_json: dict[str, typing.Any]):
        resp_json.pop("kinda_secret")
        form_data = FormData(**resp_json)

        if await self.bot.redis.get(f"mp-form:{form_data.id}"):
            return

        user_question = next(i for i in form_data.items if i["id"] == 313318916)
        username = user_question["answer"]

        username_to_search = username
        hash_split = username.split("#")
        discrim = "0"

        if len(hash_split) == 2 and hash_split[1].isdigit() and len(hash_split[1]) == 4:
            username_to_search = hash_split[0]
            discrim = hash_split[1]

        if possible_member := next(
            (
                m
                for m in self.bot.guild.members
                if m.username == username_to_search and m.discriminator == discrim
            ),
            None,
        ):
            username = possible_member.mention

        embed = ipy.Embed(
            title="Artist Form Response",
            color=self.bot.color,
            timestamp=ipy.Timestamp.utcnow(),
        )
        embed.add_field("Submitted User", username, inline=True)
        embed.add_field(
            "Submitted Form (As Pre-Filled Template)",
            f"[Link]({form_data.url})",
            inline=True,
        )

        await self.staff_chat.send(embeds=embed)
        await self.bot.redis.set(f"mp-art-form:{form_data.id}", "1")


def setup(bot: utils.MPBotBase) -> None:
    importlib.reload(utils)
    FormResponse(bot)
