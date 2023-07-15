import asyncio
import contextlib
import logging
import os
import sys
from pathlib import Path

import interactions as ipy
from dotenv import load_dotenv
from interactions.ext import prefixed_commands as prefixed

import common.utils as utils

load_dotenv()

file_location = Path(__file__).parent.absolute().as_posix()
os.environ["DIRECTORY_OF_FILE"] = file_location
os.environ["LOG_FILE_PATH"] = f"{file_location}/discord.log"


logger = logging.getLogger("mpbot")
logger.setLevel(logging.INFO)

handler = logging.FileHandler(
    filename=os.environ["LOG_FILE_PATH"], encoding="utf-8", mode="a"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

stream = logging.StreamHandler(sys.stdout)
stream.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(stream)


class MPBot(utils.MPBotBase):
    @ipy.listen("startup")
    async def on_startup(self):
        self.guild = self.get_guild(1128865913979015239)  # type: ignore
        self.fully_ready.set()

    @ipy.listen("ready")
    async def on_ready(self):
        utcnow = ipy.Timestamp.utcnow()
        time_format = f"<t:{int(utcnow.timestamp())}:f>"

        connect_msg = (
            f"Logged in at {time_format}!"
            if self.init_load == True
            else f"Reconnected at {time_format}!"
        )

        await self.owner.send(connect_msg)

        self.init_load = False

        activity = ipy.Activity.create(
            name="over Mythical Paragon", type=ipy.ActivityType.WATCHING
        )

        await self.change_presence(activity=activity)

    @ipy.listen("resume")
    async def on_resume(self):
        activity = ipy.Activity.create(
            name="over Mythical Paragon", type=ipy.ActivityType.WATCHING
        )
        await self.change_presence(activity=activity)

    async def on_error(self, source: str, error: Exception, *args, **kwargs) -> None:
        await utils.error_handle(self, error)

    async def stop(self) -> None:
        return await super().stop()


intents = ipy.Intents.ALL
mentions = ipy.AllowedMentions.all()

bot = MPBot(
    allowed_mentions=mentions,
    intents=intents,
    sync_interactions=False,
    sync_ext=False,
    fetch_members=True,
    disable_dm_commands=True,
    debug_scope=1128865913979015239,
    logger=logger,
)
bot.init_load = True
bot.color = ipy.Color(int(os.environ["BOT_COLOR"]))  # 573ae5, aka 5716709
prefixed.setup(bot)


with contextlib.suppress(ImportError):
    import uvloop

    uvloop.install()


async def start():
    bot.fully_ready = asyncio.Event()

    ext_list = utils.get_all_extensions(os.environ["DIRECTORY_OF_FILE"])
    for ext in ext_list:
        try:
            bot.load_extension(ext)
        except ipy.errors.ExtensionLoadException:
            raise

    await bot.astart(os.environ["MAIN_TOKEN"])


asyncio.run(start())
