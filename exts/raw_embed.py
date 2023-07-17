import importlib

import interactions as ipy
import orjson

import common.utils as utils


class RawEmbed(utils.Extension):
    def __init__(self, bot):
        self.bot: utils.MPBotBase = bot
        self.name = "Raw Embed"
        self.add_ext_auto_defer(enabled=False)

    @ipy.slash_command(
        "raw-embed-say",
        description="Allows you to send an embed from the raw embed JSON format.",
    )
    async def raw_embed_say(self, ctx: ipy.SlashContext):
        modal = ipy.Modal(
            ipy.InputText(
                label="Enter the embed you want to send:",
                style=ipy.TextStyles.PARAGRAPH,
                custom_id="embed-say",
            ),
            title="Raw Embed Say",
            custom_id="raw-embed-say",
        )
        await ctx.send_modal(modal)

    @ipy.context_menu(
        "Edit Embed (Raw)",
        context_type=ipy.CommandType.MESSAGE,
        default_member_permissions=ipy.Permissions.MANAGE_GUILD,
        dm_permission=False,
    )  # type: ignore
    async def raw_embed_edit(self, ctx: ipy.SlashContext):
        msg: ipy.Message = ctx.target  # type: ignore

        if not msg.embeds:
            await ctx.send("No embeds found.", ephemeral=True)
            return

        modal = ipy.Modal(
            ipy.InputText(
                label="Enter the embed you want to edit:",
                style=ipy.TextStyles.PARAGRAPH,
                value=orjson.dumps(
                    msg.embeds[0].to_dict(), option=orjson.OPT_INDENT_2
                ).decode(),
                custom_id="embed-edit",
            ),
            title="Raw Embed Edit",
            custom_id=f"raw-embed-edit|{msg.id}",
        )
        await ctx.send_modal(modal)

    @ipy.listen(ipy.events.ModalCompletion)  # type: ignore
    async def on_modal_completion(self, event: ipy.events.ModalCompletion):
        ctx = event.ctx

        if ctx.custom_id == "raw-embed-say":
            try:
                embed_dict: dict = orjson.loads(ctx.responses["embed-say"])
            except orjson.JSONDecodeError:
                await ctx.send("Could not parse the raw embed.", ephemeral=True)
                return

            await ctx.send("Sending...", ephemeral=True)
            await ctx.channel.send(embed=embed_dict)

        elif ctx.custom_id.startswith("raw-embed-edit"):
            msg_id = int(ctx.custom_id.split("|")[1])

            try:
                embed_dict: dict = orjson.loads(ctx.responses["embed-edit"])
            except orjson.JSONDecodeError:
                await ctx.send("Could not parse the raw embed.", ephemeral=True)
                return

            await ctx.send("Editing...", ephemeral=True)

            message = await ctx.channel.fetch_message(msg_id)
            if message:
                await message.edit(embed=embed_dict)
            else:
                await ctx.send("Could not get message.", ephemeral=True)
                return


def setup(bot):
    importlib.reload(utils)
    RawEmbed(bot)
