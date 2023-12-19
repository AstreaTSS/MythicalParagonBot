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
    1: "83980397fe7927c48e1cc5d1e21c3d42be9d5a38a3650e7ded95e1360b816b58ca581a61dd5af6ec108351a0420dc846909a78dcc78395aa0d401bd21e5a901a13ed7c80efbeb04ad5e83a391285bec91629842ab3ee5a304a7c1b0aa31038cf186818cd1d09b615ea5b4ec61ca45270e8fc8313fa92152d294f15c4b977dba6b26fe24088bc29302c99c81b503b20a4dc0435e9db61937f5d5b07bbadb7dc6809648893b67bc60c5949e6c93fcd1cfcf5fca067bee0a15a300292f61b42ce7ff970cc8e6afea5df0700942df18f4c2f8c33911b04a4c44ee677cd91141f5d95492a7148731e081e650abf9dbcd2242490036fab27070a4a385d6063e6ba1023a0e1229ee1d04ba95ea3a5cb1749b8e6aca28caf49ee025217db09c82cb2bedc6211c1c7f2288df5efe6afafc9bd60e41f800af683d58359936dabfbcd4e637c383e8e847aac91dda8cb3cf60bc5f77750b4ac05abc31b4f53eeaef6ab51d2daccd5909c9aceeb701d24245c97096a2f19a6838d6bc1e801f65197194ff3e608a991b3921a3bd95be153daf5b4fd9587954e93fa0bafb90518fd78650700e5c6b08ca53c336ce24872c977cac2856b6ce941ce2f6897f27ca49ea349435d66a5136cdc9d32b57ce57d04d17ebc2781c32fc59f289d1fba77f40289469a8238a50fd62cc2a9be617c0bf0bb407035da926853f101886ee32cd2a9ab0818e29c699f815a1e3940dc0bb75db7fa",
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
            choices=[ipy.SlashCommandChoice("Message 1", 1)],
        ),
        password: str = tansy.Option("The password to use."),
        salt: str = tansy.Option("The salt to use."),
    ):
        try:
            true_message = await asyncio.to_thread(
                self._actual_decrypt, message, password, salt
            )
            await ctx.send(true_message)
        except Exception:
            raise ipy.errors.BadArgument("Incorrect password or salt.") from None

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

        if len(encrypted_message) > 2000:
            await resp_ctx.send(embed=ipy.Embed(description=encrypted_message))
        else:
            await resp_ctx.send(encrypted_message)


def setup(bot: utils.MPBotBase) -> None:
    importlib.reload(utils)
    ColorsFlyingHigh(bot)
