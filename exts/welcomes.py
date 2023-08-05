import importlib

import interactions as ipy

import common.utils as utils


class WelcomeLeaves(ipy.Extension):
    def __init__(self, bot: utils.MPBotBase) -> None:
        self.bot: utils.MPBotBase = bot
        self.welcome_chan = ipy.GuildText(
            client=self.bot, id=1128876234084974703, type=ipy.ChannelType.GUILD_TEXT  # type: ignore
        )

    @ipy.listen(ipy.events.MemberAdd)
    async def member_welcome(self, event: ipy.events.MemberAdd) -> None:
        if event.guild_id == self.bot.guild.id:
            embed = ipy.Embed(
                title=self.bot.guild.name,
                description=(
                    f"Welcome, {event.member.mention}, to **{self.bot.guild.name}!** Be"
                    " sure to check out the rules at <#1128873353378275409>,"
                    " information about the KG and its world in"
                    " <#1137212762779562074>, and the application at"
                    " <#1128890650100781148>. Otherwise, feel free to take a look"
                    " around!"
                ),
                color=self.bot.color,
                timestamp=ipy.Timestamp.utcnow(),
            )
            embed.set_image(
                "https://cdn.discordapp.com/attachments/1128875291448725534/1130687853643431996/welcomegif.gif"
            )

            msg = await self.welcome_chan.send(event.member.mention, embeds=embed)
            await msg.add_reaction("👋")


def setup(bot) -> None:
    importlib.reload(utils)
    WelcomeLeaves(bot)
