import importlib

import interactions as ipy
import interactions.ext.prefixed_commands as prefixed

import common.utils as utils


class SelfRoles(utils.Extension):
    def __init__(self, bot):
        self.bot: utils.MPBotBase = bot
        self.name = "Self-Role"

        self.pronoun_roles = {
            "She/her": 1128884050858356836,
            "He/him": 1128884230001266718,
            "It/its": 1128884265602519112,
            "They/them": 1128884300297805905,
            "Neopronouns": 1128884328286396527,
            "Any Prnouns": 1128884365720567888,
            "Ask for Pronouns": 1128884400218718288,
        }

        self.pronoun_select = ipy.StringSelectMenu(
            *(
                ipy.StringSelectOption(label=k, value=f"mppronoun:{v}|{k}")
                for k, v in self.pronoun_roles.items()
            ),
            custom_id="mppronounselect",
            placeholder="Select your pronouns!",
            min_values=0,
            max_values=len(self.pronoun_roles),
        )

        self.app_status_roles: dict[str, tuple[int, str]] = {
            "Applying": (1128886764472377344, "📝"),
            "Undecided": (1128886792746192896, "❓"),
            "Spectating": (1128886813445070970, "👁️"),
        }

        self.app_status_select = ipy.StringSelectMenu(
            *(
                ipy.StringSelectOption(
                    label=k, value=f"mpappstatus:{v[0]}|{k}", emoji=v[1]
                )
                for k, v in self.app_status_roles.items()
            ),
            custom_id="mpappstatusselect",
            placeholder="Select your status!",
            min_values=0,
            max_values=1,
        )

        self.ping_roles_buttons = [
            ipy.Button(
                style=ipy.ButtonStyle.GRAY,
                emoji="🗣️",
                custom_id="mprolebutton|1128886583421055086",
            ),
            ipy.Button(
                style=ipy.ButtonStyle.GRAY,
                emoji="⛏",
                custom_id="mprolebutton|1137502788335718480",
            ),
            ipy.Button(
                style=ipy.ButtonStyle.GRAY,
                emoji="👁️",
                custom_id="mprolebutton|1128886619085222082",
            ),
            ipy.Button(
                style=ipy.ButtonStyle.GRAY,
                emoji="🤝",
                custom_id="mprolebutton|1128886651859501106",
            ),
            ipy.Button(
                style=ipy.ButtonStyle.GRAY,
                emoji="✍️",
                custom_id="mprolebutton|1128886719354261646",
            ),
            ipy.Button(
                style=ipy.ButtonStyle.GRAY,
                emoji="📊",
                custom_id="mprolebutton|1138101611307212883",
            ),
        ]

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def send_pronoun_select(self, ctx: prefixed.PrefixedContext):
        embed = ipy.Embed(
            title="Pronouns",
            description=(
                "Select the pronouns you wish to have. They will appear in your profile"
                " as a bright green role.\nAny old pronouns not re-selected will be"
                " removed."
            ),
            color=self.bot.color,
        )

        await ctx.send(embed=embed, components=self.pronoun_select)
        await ctx.message.delete()

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def send_app_status_select(self, ctx: prefixed.PrefixedContext):
        embed = ipy.Embed(
            title="Application Status",
            description=(
                "Select your status in terms of applying. They will appear in"
                " your profile as a blue role."
            ),
            color=self.bot.color,
        )

        await ctx.send(embed=embed, components=self.app_status_select)
        await ctx.message.delete()

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def send_ping_roles_select(self, ctx: prefixed.PrefixedContext):
        button_list = "\n".join(
            f"{b.emoji} - <@&{b.custom_id.removeprefix('mprolebutton|')}>"
            for b in self.ping_roles_buttons
        )

        embed = ipy.Embed(
            title="Ping Roles",
            description=(
                "Select which topics you want to be notified about.\n\nThe roles are"
                f" as follows:\n{button_list}"
            ),
            color=self.bot.color,
        )

        await ctx.send(
            embed=embed, components=ipy.spread_to_rows(self.ping_roles_buttons)
        )
        await ctx.message.delete()

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def edit_pronoun_select(
        self, ctx: prefixed.PrefixedContext, msg: ipy.Message
    ):
        embed = ipy.Embed(
            title="Pronouns",
            description=(
                "Select the pronouns you wish to have. They will appear in your profile"
                " as a bright green role.\nAny old pronouns not re-selected will be"
                " removed."
            ),
            color=self.bot.color,
        )

        await msg.edit(embed=embed, components=self.pronoun_select)
        await ctx.reply("Done!")

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def edit_app_status_select(
        self, ctx: prefixed.PrefixedContext, msg: ipy.Message
    ):
        embed = ipy.Embed(
            title="Application Status",
            description=(
                "Select your status in terms of applying. They will appear in"
                " your profile as a blue role."
            ),
            color=self.bot.color,
        )

        await msg.edit(embed=embed, components=self.app_status_select)
        await ctx.reply("Done!")

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def edit_ping_roles_select(
        self, ctx: prefixed.PrefixedContext, msg: ipy.Message
    ):
        button_list = "\n".join(
            f"{b.emoji} - <@&{b.custom_id.removeprefix('mprolebutton|')}>"
            for b in self.ping_roles_buttons
        )

        embed = ipy.Embed(
            title="Ping Roles",
            description=(
                "Select which topics you want to be notified about.\n\nThe roles are"
                f" as follows:\n{button_list}"
            ),
            color=self.bot.color,
        )

        await msg.edit(
            embed=embed, components=ipy.spread_to_rows(self.ping_roles_buttons)
        )
        await ctx.reply("Done!")

    @staticmethod
    async def process_select(
        ctx: ipy.ComponentContext,
        *,
        roles: dict[str, int] | dict[str, tuple[int, str]],
        prefix: str,
        add_text: str,
        remove_text: str,
    ):
        member = ctx.author

        if not isinstance(member, ipy.Member):
            await ctx.send("An error occured. Please try again.", ephemeral=True)
            return

        # do this weirdness since doing member.roles has a cache
        # search cost which can be expensive if there are tons of roles
        member_roles = {int(r) for r in member._role_ids}

        role_ids = list(roles.values())
        if isinstance(role_ids[0], tuple):
            role_ids = [r[0] for r in role_ids]  # type: ignore

        member_roles.difference_update(role_ids)

        if ctx.values:
            add_list = []

            for value in ctx.values:
                value: str
                split_string = value.removeprefix(f"{prefix}:").split("|")
                role = int(split_string[0])
                name = split_string[1]

                member_roles.add(role)
                add_list.append(f"`{name}`")

            await member.edit(roles=list(member_roles))
            await ctx.send(f"New {add_text}: {', '.join(add_list)}.", ephemeral=True)

        else:
            await member.edit(roles=list(member_roles))
            await ctx.send(f"{remove_text} removed.", ephemeral=True)

    @ipy.listen(ipy.events.Component)
    async def component_handle(self, event: ipy.events.Component):
        ctx = event.ctx

        if ctx.custom_id == "mppronounselect":
            await self.process_select(
                ctx,
                roles=self.pronoun_roles,
                prefix="mppronoun",
                add_text="pronouns",
                remove_text="All pronouns",
            )
        elif ctx.custom_id == "mpappstatusselect":
            await self.process_select(
                ctx,
                roles=self.app_status_roles,
                prefix="mpappstatus",
                add_text="status",
                remove_text="Status",
            )
        elif ctx.custom_id == "mppingrolesselect":
            await self.process_select(
                ctx,
                roles=self.ping_roles,
                prefix="mppingroles",
                add_text="ping roles",
                remove_text="Ping roles",
            )

    @ipy.listen(ipy.events.ButtonPressed)
    async def button_handle(self, event: ipy.events.ButtonPressed):
        ctx = event.ctx

        if ctx.custom_id.startswith("mprolebutton|"):
            member = ctx.author
            if not isinstance(member, ipy.Member):
                await ctx.send("An error occured. Please try again.", ephemeral=True)
                return

            role_id = int(ctx.custom_id.removeprefix("rolebutton|"))
            role = await self.bot.guild.fetch_role(role_id)
            if not role:
                await ctx.send("An error occured. Please try again.", ephemeral=True)
                return

            if member.has_role(role):
                await member.remove_role(role)
                await ctx.send(f"Removed {role.mention}.", ephemeral=True)
            else:
                await member.add_role(role)
                await ctx.send(f"Added {role.mention}.", ephemeral=True)


def setup(bot):
    importlib.reload(utils)
    SelfRoles(bot)
