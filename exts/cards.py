import importlib
import re
import time

import interactions as ipy
import tansy
from prisma import models
from prisma.enums import Status

import common.utils as utils


CARD_VALIDATE_REGEX = re.compile(
    r"\*\*Name\*\*: (?P<name>[^\n]+)\n\*\*Talent\*\*:"
    r" (?P<talent>[^\n]+)\n\*\*Status\*\*: (?P<status>\S+)\n\n\*\*Age\*\*:"
    r" (?P<age>\S+)\n\*\*Weight\*\*:"
    r" (?P<weight>\d+).*\n\*\*Height\*\*: (?P<height>\d+).*\n\*\*Pronouns\*\*:"
    r" (?P<pronouns>[^\n]+)\n\n\*\*Likes\*\*: (?P<likes>[^\n]+)\n\*\*Dislikes\*\*:"
    r" (?P<dislikes>[^\n]+)\n\*\*Fears\*\*: (?P<fears>[^\n]+)\n\*\*OC By\*\*:"
    r" <@(?P<oc_by>\d+)>\n\n\*\*Image URL\*\*: (?P<image_url>\S+)"
)

NAME_REGEX = re.compile(r"\*\*Name\*\*: (?P<name>[^\n]+)")
STATUS_REGEX = re.compile(r"\*\*Status\*\*: (?P<status>\S+)")
TALENT_REGEX = re.compile(r"\*\*Talent\*\*: (?P<talent>[^\n]+)")
AGE_REGEX = re.compile(r"\*\*Age\*\*: (?P<age>\S+)")
WEIGHT_SEARCH_REGEX = re.compile(r"\*\*Weight\*\*: (?P<weight>\d+)")
WEIGHT_REGEX = re.compile(r"\*\*Weight\*\*: (?P<weight>[^\n]+)")
HEIGHT_SEARCH_REGEX = re.compile(r"\*\*Height\*\*: (?P<height>\d+)")
HEIGHT_REGEX = re.compile(r"\*\*Height\*\*: (?P<height>[^\n]+)")
PRONOUNS_REGEX = re.compile(r"\*\*Pronouns\*\*: (?P<pronouns>[^\n]+)")
LIKES_REGEX = re.compile(r"\*\*Likes\*\*: (?P<likes>[^\n]+)")
DISLIKES_REGEX = re.compile(r"\*\*Dislikes\*\*: (?P<dislikes>[^\n]+)")
FEARS_REGEX = re.compile(r"\*\*Fears\*\*: (?P<fears>[^\n]+)")
# OC_BY_REGEX = re.compile(r"\*\*OC By\*\*: <@(?P<oc_by>\d+)>")
IMAGE_URL_REGEX = re.compile(r"\*\*Image URL\*\*: (?P<image_url>\S+)")

HEIGHT_FEET_INCHES_REGEX = re.compile(r"(\d)' (\d+)")


def to_kg(lbs: int) -> int:
    return round(lbs / 2.2046)


def inches_display(inches: int) -> str:
    feet = inches // 12
    inches %= 12
    return f"{feet}' {inches}\""


def to_cm(inches: int) -> int:
    return round(inches * 2.54)


STATUS_COLOR: dict[Status, ipy.Color] = {
    Status.ALIVE: ipy.Color("#573ae5"),
    Status.DEAD: ipy.RoleColors.RED,
    Status.MISSING: ipy.RoleColors.LIGHT_GRAY,
}


async def card_embed(bot: utils.MPBotBase, card: models.CharacterCard):
    user = await bot.cache.fetch_user(card.user_id)
    embed = ipy.Embed(color=STATUS_COLOR[card.status])

    if card.talent:
        embed.title = f"{card.oc_name}, the Ultimate {card.talent}"
    else:
        embed.title = card.oc_name

    string_builder: list[str] = [
        "**Basic Information**",
        f"**Age**: {card.age}",
        f"**Weight**: {card.weight} lbs ({to_kg(card.weight)} kg)",
        f"**Height**: {inches_display(card.height)} ({to_cm(card.height)} cm)",
        f"**Pronouns**: {card.pronouns}",
    ]

    string_builder.extend(
        (
            "\n**Other Information**",
            f"**Likes**: {card.likes}",
            f"**Dislikes**: {card.dislikes}",
            f"**Fears**: {card.fears}",
            f"**OC By**: {user.mention} ({user.tag})",
        )
    )

    embed.description = "\n".join(string_builder)
    embed.set_image(url=card.image_url)
    embed.set_footer(f"Status: {card.status.capitalize()}")
    return embed


CARD_BUTTONS = ipy.spread_to_rows(
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Name",
        custom_id="card-edit-name",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Talent",
        custom_id="card-edit-talent",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Status",
        custom_id="card-edit-status",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Age",
        custom_id="card-edit-age",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Weight",
        custom_id="card-edit-weight",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Height",
        custom_id="card-edit-height",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Pronouns",
        custom_id="card-edit-pronouns",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Likes",
        custom_id="card-edit-likes",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Dislikes",
        custom_id="card-edit-dislikes",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Fears",
        custom_id="card-edit-fears",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.BLUE,
        label="Edit Image URL",
        custom_id="card-edit-image-url",
    ),
    ipy.Button(
        style=ipy.ButtonStyle.GREEN,
        label="Submit",
        custom_id="card-submit",
    ),
)


class Cards(utils.Extension):
    def __init__(self, bot):
        self.bot: utils.MPBotBase = bot
        self.card_channel = ipy.GuildText(client=self.bot, id=1129636634590195793, type=ipy.ChannelType.GUILD_TEXT)  # type: ignore

    @ipy.slash_command(
        name="update-card-channel",
        default_member_permissions=ipy.Permissions.MANAGE_GUILD,
    )
    async def update_card_channel(self, ctx: ipy.SlashContext):
        await ctx.defer()

        cards = await models.CharacterCard.prisma().find_many(
            where={"type": 1}, order={"oc_name": "asc"}
        )

        card_embeds = [await card_embed(self.bot, card) for card in cards]

        bulk_delete: list[ipy.Message] = []
        fourteen_days_ago = (
            int((time.time() - 1209600) * 1000.0 - ipy.const.DISCORD_EPOCH) << 22
        )

        async for message in self.card_channel.history(limit=100):
            if message.author == self.bot.user:
                if message.id > fourteen_days_ago:
                    bulk_delete.append(message)
                else:
                    await message.delete()

        if bulk_delete:
            await self.card_channel.delete_messages(bulk_delete)

        for embed in card_embeds:
            await self.card_channel.send(embeds=embed)

        final_content = (
            "All participant cards should be in alphabetical order.\nIf a user's"
            " mention is just a bunch of numbers, that's a Discord glitch that we can't"
            " fix - sorry about that!"
        )
        final_content += "\n\nIf you want to update your card, please DM Astrea."

        await self.card_channel.send(
            content=final_content,
            embeds=ipy.Embed(
                footer=ipy.EmbedFooter(text="Last updated"),
                timestamp=ipy.Timestamp.utcnow(),
            ),
        )

        await ctx.send("Updated the card channel!")

    @tansy.slash_command(
        name="create-card", default_member_permissions=ipy.Permissions.MANAGE_GUILD
    )
    async def create_card(
        self,
        ctx: ipy.SlashContext,
        user: ipy.Member = tansy.Option("The user who created the OC."),
    ):
        if await models.CharacterCard.prisma().count(
            where={"user_id": user.id, "type": 1}
        ):
            raise ipy.errors.BadArgument("That user already has a card.")

        content_builder: list[str] = [
            "**Name**: N/A",
            "**Talent**: N/A",
            "**Status**: Alive",
            "\n**Age**: N/A",
            "**Weight**: N/A lbs (N/A kg)",
            "**Height**: N/A in (N/A cm)",
            "**Pronouns**: N/A",
            "\n**Likes**: N/A",
            "**Dislikes**: N/A",
            "**Fears**: N/A",
            f"**OC By**: {user.mention}",
            "\n**Image URL**: N/A",
        ]

        await ctx.send(
            "\n".join(content_builder),
            components=CARD_BUTTONS,
            allowed_mentions=ipy.AllowedMentions.none(),
        )

    @tansy.slash_command(
        name="edit-card", default_member_permissions=ipy.Permissions.MANAGE_GUILD
    )
    async def edit_card(
        self,
        ctx: ipy.SlashContext,
        user: ipy.Member = tansy.Option("The user who created the OC."),
    ):
        card = await models.CharacterCard.prisma().find_first(
            where={"user_id": user.id, "type": 1}
        )

        if not card:
            raise ipy.errors.BadArgument("That user does not have a card.")

        content_builder: list[str] = [
            f"**Name**: {card.oc_name}",
            f"**Talent**: {card.talent}",
            f"**Status**: {card.status.capitalize()}",
            f"\n**Age**: {card.age}",
            f"**Weight**: {card.weight} lbs ({to_kg(card.weight)} kg)",
            (
                f"**Height**: {card.height} in ({inches_display(card.height)},"
                f" {to_cm(card.height)} cm)"
            ),
            f"**Pronouns**: {card.pronouns}",
            f"\n**Likes**: {card.likes}",
            f"**Dislikes**: {card.dislikes}",
            f"**Fears**: {card.fears}",
            f"**OC By**: {user.mention}",
            f"\n**Image URL**: {card.image_url}",
        ]

        await ctx.send(
            "\n".join(content_builder),
            components=CARD_BUTTONS,
            allowed_mentions=ipy.AllowedMentions.none(),
        )

    @ipy.component_callback("card-edit-name")
    async def card_edit_name_button(self, ctx: ipy.ComponentContext):
        name = ipy.MISSING
        if a_match := NAME_REGEX.search(ctx.message.content):
            name = a_match.group("name")

        if name == "N/A":
            name = ipy.MISSING

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(label="Name:", custom_id="name", value=name),
                title="Edit Name",
                custom_id=f"card-edit-name|{ctx.message_id}",
            ),
        )

    @ipy.component_callback("card-edit-talent")
    async def card_edit_talent_button(self, ctx: ipy.ComponentContext):
        talent = ipy.MISSING
        if a_match := TALENT_REGEX.search(ctx.message.content):
            talent = a_match.group("talent")

        if talent == "N/A":
            talent = ipy.MISSING

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(label="Talent:", custom_id="talent", value=talent),
                title="Edit Talent",
                custom_id=f"card-edit-talent|{ctx.message_id}",
            ),
        )

    @ipy.component_callback("card-edit-status")
    async def card_edit_status_button(self, ctx: ipy.ComponentContext):
        a_match = STATUS_REGEX.search(ctx.message.content)
        if not a_match:
            return await ctx.send("Could not parse the status.", ephemeral=True)

        status = a_match.group("status")

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(label="Status:", custom_id="status", value=status),
                title="Edit Status",
                custom_id=f"card-edit-status|{ctx.message_id}",
            ),
        )

    @ipy.component_callback("card-edit-age")
    async def card_edit_age_button(self, ctx: ipy.ComponentContext):
        age = ipy.MISSING
        if a_match := AGE_REGEX.search(ctx.message.content):
            age = a_match.group("age")

        if age == "N/A":
            age = ipy.MISSING

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(label="Age:", custom_id="age", value=age),
                title="Edit Age",
                custom_id=f"card-edit-age|{ctx.message_id}",
            ),
        )

    @ipy.component_callback("card-edit-weight")
    async def card_edit_weight_button(self, ctx: ipy.ComponentContext):
        weight = ipy.MISSING
        if a_match := WEIGHT_SEARCH_REGEX.search(ctx.message.content):
            weight = a_match.group("weight")

        if weight == "N/A":
            weight = ipy.MISSING

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(
                    label="Weight:",
                    custom_id="weight",
                    value=weight,
                    placeholder="No decimals, please. Use pounds.",
                ),
                title="Edit Weight",
                custom_id=f"card-edit-weight|{ctx.message_id}",
            ),
        )

    @ipy.component_callback("card-edit-height")
    async def card_edit_height_button(self, ctx: ipy.ComponentContext):
        height = ipy.MISSING
        if a_match := HEIGHT_SEARCH_REGEX.search(ctx.message.content):
            height = a_match.group("height")

        if height == "N/A":
            height = ipy.MISSING

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(
                    label="Height:",
                    custom_id="height",
                    value=height,
                    placeholder="No decimals, please. Use inches or feet' inches\".",
                ),
                title="Edit Height",
                custom_id=f"card-edit-height|{ctx.message_id}",
            ),
        )

    @ipy.component_callback("card-edit-pronouns")
    async def card_edit_pronouns_button(self, ctx: ipy.ComponentContext):
        pronouns = ipy.MISSING
        if a_match := PRONOUNS_REGEX.search(ctx.message.content):
            pronouns = a_match.group("pronouns")

        if pronouns == "N/A":
            pronouns = ipy.MISSING

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(label="Pronouns:", custom_id="pronouns", value=pronouns),
                title="Edit Pronouns",
                custom_id=f"card-edit-pronouns|{ctx.message_id}",
            ),
        )

    @ipy.component_callback("card-edit-likes")
    async def card_edit_likes_button(self, ctx: ipy.ComponentContext):
        likes = ipy.MISSING
        if a_match := LIKES_REGEX.search(ctx.message.content):
            likes = a_match.group("likes")

        if likes == "N/A":
            likes = ipy.MISSING

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(label="Likes:", custom_id="likes", value=likes),
                title="Edit Likes",
                custom_id=f"card-edit-likes|{ctx.message_id}",
            ),
        )

    @ipy.component_callback("card-edit-dislikes")
    async def card_edit_dislikes_button(self, ctx: ipy.ComponentContext):
        dislikes = ipy.MISSING
        if a_match := DISLIKES_REGEX.search(ctx.message.content):
            dislikes = a_match.group("dislikes")

        if dislikes == "N/A":
            dislikes = ipy.MISSING

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(label="Dislikes:", custom_id="dislikes", value=dislikes),
                title="Edit Dislikes",
                custom_id=f"card-edit-dislikes|{ctx.message_id}",
            ),
        )

    @ipy.component_callback("card-edit-fears")
    async def card_edit_fears_button(self, ctx: ipy.ComponentContext):
        fears = ipy.MISSING
        if a_match := FEARS_REGEX.search(ctx.message.content):
            fears = a_match.group("fears")

        if fears == "N/A":
            fears = ipy.MISSING

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(label="Fears:", custom_id="fears", value=fears),
                title="Edit Fears",
                custom_id=f"card-edit-fears|{ctx.message_id}",
            ),
        )

    @ipy.component_callback("card-edit-image-url")
    async def card_edit_image_url_button(self, ctx: ipy.ComponentContext):
        image_url = ipy.MISSING
        if a_match := IMAGE_URL_REGEX.search(ctx.message.content):
            image_url = a_match.group("image_url")

        if image_url == "N/A":
            image_url = ipy.MISSING

        await ctx.send_modal(
            ipy.Modal(
                ipy.ShortText(
                    label="Image URL:", custom_id="image_url", value=image_url
                ),
                title="Edit Image URL",
                custom_id=f"card-edit-image-url|{ctx.message_id}",
            ),
        )

    @ipy.listen(ipy.events.ModalCompletion)
    async def modal_listen(self, event: ipy.events.ModalCompletion):
        ctx = event.ctx

        if not ctx.custom_id.startswith("card"):
            return

        await ctx.defer(ephemeral=True)

        message_id = int(ctx.custom_id.split("|")[1])
        message = await ctx.channel.fetch_message(message_id)
        if not message:
            return await ctx.send("Could not get message.", ephemeral=True)

        new_content = message.content

        if ctx.custom_id.startswith("card-edit-name"):
            new_content = NAME_REGEX.sub(
                f"**Name**: {ctx.responses['name']}", message.content
            )
        elif ctx.custom_id.startswith("card-edit-talent"):
            new_content = TALENT_REGEX.sub(
                f"**Talent**: {ctx.responses['talent']}", message.content
            )
        elif ctx.custom_id.startswith("card-edit-status"):
            try:
                true_status = Status[ctx.responses["status"].upper()]
                new_content = STATUS_REGEX.sub(
                    f"**Status**: {true_status.name.capitalize()}",
                    message.content,
                )
            except KeyError:
                return await ctx.send("Invalid status.", ephemeral=True)
        elif ctx.custom_id.startswith("card-edit-age"):
            new_content = AGE_REGEX.sub(
                f"**Age**: {ctx.responses['age']}", message.content
            )
        elif ctx.custom_id.startswith("card-edit-weight"):
            if not ctx.responses["weight"].isdigit():
                return await ctx.send("Weight must be a number.", ephemeral=True)

            new_content = WEIGHT_REGEX.sub(
                (
                    f"**Weight**: {ctx.responses['weight']} lbs"
                    f" ({to_kg(int(ctx.responses['weight']))} kg)"
                ),
                message.content,
            )
        elif ctx.custom_id.startswith("card-edit-height"):
            height = ctx.responses["height"]

            if a_match := HEIGHT_FEET_INCHES_REGEX.match(height):
                feet = int(a_match.group(1))
                inches = int(a_match.group(2))
                height = str(feet * 12 + inches)

            if not height.isdigit():
                return await ctx.send("Height must be a number.", ephemeral=True)

            new_content = HEIGHT_REGEX.sub(
                (
                    f"**Height**: {height} in"
                    f" ({inches_display(int(height))}, {to_cm(int(height))} cm)"
                ),
                message.content,
            )
        elif ctx.custom_id.startswith("card-edit-pronouns"):
            new_content = PRONOUNS_REGEX.sub(
                f"**Pronouns**: {ctx.responses['pronouns']}", message.content
            )
        elif ctx.custom_id.startswith("card-edit-likes"):
            new_content = LIKES_REGEX.sub(
                f"**Likes**: {ctx.responses['likes']}", message.content
            )
        elif ctx.custom_id.startswith("card-edit-dislikes"):
            new_content = DISLIKES_REGEX.sub(
                f"**Dislikes**: {ctx.responses['dislikes']}", message.content
            )
        elif ctx.custom_id.startswith("card-edit-fears"):
            new_content = FEARS_REGEX.sub(
                f"**Fears**: {ctx.responses['fears']}", message.content
            )
        elif ctx.custom_id.startswith("card-edit-image-url"):
            new_content = IMAGE_URL_REGEX.sub(
                f"**Image URL**: {ctx.responses['image_url']}", message.content
            )

        await message.edit(content=new_content)
        await ctx.send("Edited.", ephemeral=True)

    @ipy.component_callback("card-submit")
    async def submit_card(self, ctx: ipy.ComponentContext):
        await ctx.defer(ephemeral=True)

        if not (a_match := CARD_VALIDATE_REGEX.match(ctx.message.content)):
            return await ctx.send("Could not parse the card.", ephemeral=True)

        name = a_match.group("name")
        talent = a_match.group("talent")
        status = Status[a_match.group("status").upper()]
        age = a_match.group("age")
        weight = int(a_match.group("weight"))
        height = int(a_match.group("height"))
        pronouns = a_match.group("pronouns")
        likes = a_match.group("likes")
        dislikes = a_match.group("dislikes")
        fears = a_match.group("fears")
        oc_by = int(a_match.group("oc_by"))
        image_url = a_match.group("image_url")

        if "N/A" in (
            name,
            talent,
            age,
            pronouns,
            oc_by,
            image_url,
        ):
            return await ctx.send("One or more fields is missing.", ephemeral=True)

        if talent == "None":
            talent = None

        if not await models.CharacterCard.prisma().count(
            where={"user_id": oc_by, "type": 1}
        ):
            await models.CharacterCard.prisma().create(
                data={
                    "user_id": oc_by,
                    "oc_name": name,
                    "talent": talent,
                    "status": status,
                    "age": age,
                    "weight": weight,
                    "height": height,
                    "pronouns": pronouns,
                    "likes": likes,
                    "dislikes": dislikes,
                    "fears": fears,
                    "image_url": image_url,
                    "type": 1,
                },
            )

            await ctx.send("Added!", ephemeral=True)
        else:
            await models.CharacterCard.prisma().update_many(
                where={"user_id": oc_by, "type": 1},
                data={
                    "oc_name": name,
                    "talent": talent,
                    "status": status,
                    "age": age,
                    "weight": weight,
                    "height": height,
                    "pronouns": pronouns,
                    "likes": likes,
                    "dislikes": dislikes,
                    "fears": fears,
                    "image_url": image_url,
                },
            )

            await ctx.send("Updated!", ephemeral=True)

        await ctx.message.delete()


def setup(bot: utils.MPBotBase) -> None:
    importlib.reload(utils)
    Cards(bot)
