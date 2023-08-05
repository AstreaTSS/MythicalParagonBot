import asyncio
import importlib
import subprocess
import time
from importlib.metadata import version as _v

import interactions as ipy

import common.utils as utils

IPY_VERSION = _v("discord-py-interactions")


class OtherCMDs(utils.Extension):
    def __init__(self, bot: utils.MPBotBase):
        self.name = "General"
        self.bot: utils.MPBotBase = bot

    @ipy.slash_command(
        "ping",
        description=(
            "Pings the bot. Great way of finding out if the bot's working correctly,"
            " but has no real use."
        ),
    )
    async def ping(self, ctx: ipy.InteractionContext) -> None:
        start_time = time.perf_counter()
        ping_discord = round((self.bot.latency * 1000), 2)

        mes = await ctx.send(
            f"Pong!\n`{ping_discord}` ms from Discord.\nCalculating personal ping..."
        )

        end_time = time.perf_counter()
        ping_personal = round(((end_time - start_time) * 1000), 2)

        await ctx.edit(
            message=mes,
            content=(
                f"Pong!\n`{ping_discord}` ms from Discord.\n`{ping_personal}` ms"
                " personally."
            ),
        )

    @ipy.slash_command("about", description="Gives information about the bot.")
    async def about(self, ctx: ipy.InteractionContext):
        about_msg = (
            f"Hello! I'm the helper bot for **{self.bot.guild.name}**, doing various"
            " things around the server. I probably don't have anything useful for you,"
            " but feel free to poke around!"
        )

        about_embed = ipy.Embed(
            title="About",
            color=self.bot.color,
            description=about_msg,
        )
        about_embed.set_thumbnail(
            ctx.guild.me.display_avatar.url
            if ctx.guild
            else self.bot.user.display_avatar.url
        )

        command_num = len(self.bot.application_commands) + len(
            self.bot.prefixed.commands
        )

        about_embed.add_field(
            name="Stats:",
            value="\n".join(
                (
                    f"Servers: {len(self.bot.guilds)}",
                    f"Commands: {command_num} ",
                    (
                        "Startup Time:"
                        f" {ipy.Timestamp.fromdatetime(self.bot.start_time).format(ipy.TimestampStyles.RelativeTime)}"
                    ),
                    (
                        "Interactions.py Version:"
                        f" [{IPY_VERSION}](https://github.com/interactions-py/interactions.py/tree/{IPY_VERSION})"
                    ),
                    "Made By: [AstreaTSS](https://github.com/AstreaTSS)",
                )
            ),
        )

        links = [
            "Source Code: [Link](https://github.com/AstreaTSS/MythicalParagonBot)",
            "Server Invite: [Link](https://discord.gg/WtBjBMMjjJ)",
        ]

        about_embed.add_field(
            name="Links:",
            value="\n".join(links),
        )
        about_embed.timestamp = ipy.Timestamp.utcnow()

        await ctx.send(embed=about_embed)


def setup(bot):
    importlib.reload(utils)
    OtherCMDs(bot)
