import importlib

import interactions as ipy
import interactions.ext.prefixed_commands as prefixed

import common.utils as utils


class SelfRoles(utils.Extension):
    def __init__(self, bot):
        self.bot: utils.MPBotBase = bot
        self.name = "Self-Role"

        self.pronoun_roles = {
            "She/Her": 1128884050858356836,
            "He/Him": 1128884230001266718,
            "It/Its": 1128884265602519112,
            "They/Them": 1128884300297805905,
            "Neopronouns": 1128884328286396527,
            "Any Pronouns": 1128884365720567888,
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

        self.kg_sepctator_button = ipy.Button(
            style=ipy.ButtonStyle.BLUE,
            label="Toggle KG Spectator",
            custom_id="mprolebutton|1160697812212797480",
        )

        self.ping_roles: dict[str, tuple[int, str, str | None]] = {
            "Announcement Ping": (1128886583421055086, "🗣️", None),
            "Minecraft Server Ping": (1137502788335718480, "⛏", None),
            "Teaser Ping": (1128886619085222082, "👁️", None),
            "Partner Ping": (1128886651859501106, "🤝", None),
            "Roleplay Ping": (
                1128886719354261646,
                "✍️",
                "Note: will be pinged frequently during the RP.",
            ),
            "OC Poll Ping": (
                1138101611307212883,
                "📊",
                "Note: will be pinged frequently during applications.",
            ),
        }

        self.ping_roles_select = ipy.StringSelectMenu(
            *(
                ipy.StringSelectOption(
                    label=k,
                    value=f"mppingroles:{v[0]}|{k}",
                    emoji=v[1],
                    description=v[2],
                )
                for k, v in self.ping_roles.items()
            ),
            custom_id="mppingrolesselect",
            placeholder="Select your ping roles!",
            min_values=0,
            max_values=len(self.ping_roles),
        )

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def send_pronoun_select(self, ctx: prefixed.PrefixedContext):
        embed = ipy.Embed(
            title="Pronouns",
            description=(
                "Select the pronouns you wish to have. They will appear in your profile"
                " as a bright green role.\n*Any old pronouns not re-selected will be"
                " removed.*"
            ),
            color=self.bot.color,
        )

        await ctx.send(embed=embed, components=self.pronoun_select)
        await ctx.message.delete()

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def send_kg_spectator_button(self, ctx: prefixed.PrefixedContext):
        embed = ipy.Embed(
            title="KG Spectator Role",
            description=(
                "If you wish to spectate the KG and aren't in the game, you can toggle"
                " the KG Spectator role through this button."
            ),
            color=self.bot.color,
        )

        await ctx.send(embed=embed, components=self.kg_sepctator_button)
        await ctx.message.delete()

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def send_ping_roles_select(self, ctx: prefixed.PrefixedContext):
        embed = ipy.Embed(
            title="Ping Roles",
            description=(
                "Select which topics you want to be notified about.\n*Any old ping"
                " roles not re-selected will be removed.*"
            ),
            color=self.bot.color,
        )

        await ctx.send(
            embed=embed,
            components=self.ping_roles_select,
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
                " as a bright green role.\n*Any old pronouns not re-selected will be"
                " removed.*"
            ),
            color=self.bot.color,
        )

        await msg.edit(embed=embed, components=self.pronoun_select)
        await ctx.reply("Done!")

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def edit_kg_spectator_button(
        self, ctx: prefixed.PrefixedContext, msg: ipy.Message
    ):
        embed = ipy.Embed(
            title="KG Spectator Role",
            description=(
                "If you wish to spectate the KG and aren't in the game, you can toggle"
                " the KG Spectator role through this button."
            ),
            color=self.bot.color,
        )

        await msg.edit(embed=embed, components=self.kg_sepctator_button)
        await ctx.reply("Done!")

    @prefixed.prefixed_command()
    @utils.proper_permissions()
    async def edit_ping_roles_select(
        self, ctx: prefixed.PrefixedContext, msg: ipy.Message
    ):
        embed = ipy.Embed(
            title="Ping Roles",
            description=(
                "Select which topics you want to be notified about.\n*Any old ping"
                " roles not re-selected will be removed.*"
            ),
            color=self.bot.color,
        )

        await msg.edit(
            embed=embed,
            components=self.ping_roles_select,
        )
        await ctx.reply("Done!")

    async def process_select(
        self,
        ctx: ipy.ComponentContext,
        *,
        roles: dict[str, int]
        | dict[str, tuple[int, str]]
        | dict[str, tuple[int, str, str | None]],
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

        removed_roles = member_roles.intersection(role_ids)
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
                removed_roles.discard(role)

            removed_roles_str = ", ".join(
                f"`{self.bot.guild.get_role(r).name}`" for r in removed_roles
            )
            if removed_roles_str:
                removed_roles_str = f"\nRemoved: {removed_roles_str}"

            await member.edit(roles=list(member_roles))
            await ctx.send(
                f"New {add_text}: {', '.join(add_list)}.{removed_roles_str}",
                ephemeral=True,
            )

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

            role_id = int(ctx.custom_id.removeprefix("mprolebutton|"))
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
