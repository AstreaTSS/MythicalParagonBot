import asyncio
import importlib
import os

import interactions as ipy
import tansy
from argon2 import PasswordHasher
from argon2.exceptions import HashingError
from Crypto.Cipher import AES

import common.utils as utils

ENCRYPTED_MESSAGE_MAP = {
    0: "37ee7b1f2e089cf534a3cf5712545a1f24075dbc5e324f5d5908d8e908bb6ffa4417ca4f8964b774",
}

ph = PasswordHasher()


class ColorsFlyingHigh(utils.Extension):
    def _actual_decrypt(self, message_num: int, password: str, salt: str) -> str:
        key = ph.hash(password, salt=salt.encode("utf-8"))
        cipher = AES.new(
            os.environ["ENCRYPTION_KEY"].encode("utf-8"),
            AES.MODE_EAX,
            nonce=key.encode("utf-8"),
        )
        decrypted_msg = cipher.decrypt(
            bytes.fromhex(ENCRYPTED_MESSAGE_MAP[message_num])
        )
        return decrypted_msg.decode("utf-8")

    @tansy.slash_command(
        dm_permission=False, description="Attempt to decrypt a message."
    )
    async def decrypt(
        self,
        ctx: ipy.SlashContext,
        message: int = tansy.Option(
            "The message to decrypt.",
            choices=[ipy.SlashCommandChoice("Test Message", 0)],
        ),
        password: str = tansy.Option("The password to use."),
        salt: str = tansy.Option("The salt to use."),
    ):
        try:
            true_message = await asyncio.to_thread(
                self._actual_decrypt, message, password, salt
            )
            await ctx.send(true_message)
        except HashingError | ValueError | UnicodeDecodeError:
            await ctx.send("Invalid password or salt.")

    def _actual_encrypt(self, message: str, password: str, salt: str) -> str:
        ph = PasswordHasher()
        key = ph.hash(password, salt=salt.encode("utf-8"))

        cipher = AES.new(
            os.environ["ENCRYPTION_KEY"].encode("utf-8"),
            AES.MODE_EAX,
            nonce=key.encode("utf-8"),
        )
        encrypted_msg = cipher.encrypt(message.encode("utf-8"))
        return encrypted_msg.hex()

    @tansy.slash_command(
        default_member_permissions=ipy.Permissions.ADMINISTRATOR,
        dm_permission=False,
        description="Sends an encrypted message.",
    )
    async def encrypt(
        self,
        ctx: ipy.SlashContext,
        password: str = tansy.Option("The password to use."),
        salt: str = tansy.Option("The salt to use."),
    ):
        modal = ipy.Modal(
            ipy.ParagraphText(
                label="Input the message to encrypt.", custom_id="message"
            ),
            title="Encrypt Message",
        )

        await ctx.send_modal(modal)
        resp_ctx = await self.bot.wait_for_modal(modal, ctx.author)

        encrypted_message = await asyncio.to_thread(
            self._actual_encrypt, resp_ctx.responses["message"], password, salt
        )
        await resp_ctx.send(encrypted_message)


def setup(bot: utils.MPBotBase) -> None:
    importlib.reload(utils)
    ColorsFlyingHigh(bot)
