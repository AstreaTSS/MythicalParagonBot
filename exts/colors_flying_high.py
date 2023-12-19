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
    2: "aae9934e56b900983d4973422fcf27401b34b493b056364c5f64c4e2fd455f3d51fbbbe2f806ae6ed1e2c22be8df6172d2bfe3c7a2e906180381d08d257e9715867981dbc2947023fc9f98f64f00bfb94b0f24b226d4a4d51753290e4b6c4554905827a233a7a148a1d94f29cfcf7c2f9e7e1b265f232d357db6a0c95c73dd6a821322d070aa037e3cd79230bd484209992eff695096e519a60da44124f20cae5591eea2edead0966abc43b7fc5fd62f280b7b39a07b805e42b5891ae9f5a6d228ee7fb3e1158183550c03fdcdab88bdbc2c40be75527f19272d7c4e782a15ecd5ec1fd03811173785d2fa09c1784860193b7054d7cd788f4603e13cf992e0f247d9947d38bdb9cd3e5279a6445a7785a37960e3c0aaa744b24f5edf9990084a7716de73cafc1e4549195751d81966c0be9e9eec04b112401e9a957104d63b657df19595cd47df66527efe2e636630da033c813bd497bf84448fc6bfb69876f491c1da63a5f5a28cda6047d02165cb7c1f8d52858c784e6fc414c7c9043f5d765bd546240fbbcee3cdf9a8ccaa71623bdcced38ba4b7ef8a194ea1b4d6bb55ccc3e656c92432d1a10ec8c1b1a522f83e3255eb71a23ca46660298e88565d215d828faeb7bc2937b577660e4115504f2bccbb4782a5a4b2cdca5495a1d23f54417285b07a51ca05a6d8d3219ae2cc95d1e057b9acd589c0f1c9c66711c8f6aefcbbdbe655a45535173186c8afd74834bfb020353db4f732a9bf438588c707385bd5aefd084addf8e7c689bc0a5fdee9110ec79a5ba87fa3b1f35b622a574d8d451ce642496e9705fc584d36deafe2a64385fc71c4456dae6212ae341ebdb12040bea314447c08fa40fa73649392d9f8fc789c4a3e22fa5e5821c7a7742aa5fcda3eb9a8ef3f602ce42ec268baced2af200866c962dacdc2086bb591d709aea28f719890b4313d16550d1e23417059b49caee04ce4cf3baf380c54f535fec0ddad12dbb7cd9598818fa49246eb46edcdc690c97a126e04742313f57a227dd86b2c131e8a75a4f302337a4790ba2271bd16e5a899e41d9bef56c71eac5a6864416adbfef6c17c6f9c6dfddb44e590ca14d0eef56b836faf38621e1c8aeef8333bfe40bbce024546b30cd94adeab4dc4bf8a87696acb63c6bf1f36f2ae1ffed637172a38c161636b3d343ac3e388a9a889ea804dcb9e970aaf0d59ebb5330fab4b89f31450f8ba6d27368e1dc7ad7f76d64112d9eb393c714115cd8f895653311d3e170cb2eac90248c6ec55f8cd8f5d03ecf4213618e01dd4eb084aeb7f76d074a91d7035c64047c15df1c957e09d8dfefd494200d12edfcfdfa72e4a79b883a10a0f2c0db93c0d1ea1f50639926b7c525758acaca19467bc13617a2362ddfcfe06b0055048243161f3226eb233ef2ace0c19b8ef170fb636a511872a85714dd0c154ed78b344c63b48f778ccf2029151fad06b994c0f8657e896d63ca97cb6b29ee682fd9b6e8151578f0fa5dbaad96c3354022c26b1cbfb04e59868dab0627893ec34a47800bac646b7c67be50972faa5fb564a3137c794487d4ab9053adfece25b3f116dd69fc8b6410d18c7a384eeff588a58668928884b12b95a19e873ece7205de483e9da3c2fd8bbb6f5ddf66eaef4e464124e07a39e644bc945b0c6dfefabb3568de2da03108ca6bc822f9e0ad4bd2c0f38f6f8bdad3eba55da69a11ac06b1b99cb838db4033d241cd12c03e7dceb4fa660539d2447212d8a093185e592b04c2fd67b0914519b43bd251750e6c9aa501793209f17ecba993542b75b1cdcb25fff5e26b01853c68d4f24b3bae2be18028072731ef23e5e01e0d02b26f2adf10b59fb68a4e6429fcfe2fe3c009c083100b90798c3955174b2d285f3df742d070a9e75752fe04f8804293f757f2aadf57788924f695619db0e5608122241660b05aeaafe4916e1e12271bcc58baf385326c29002c4a0951d6da8808ffda8465875e4fa382fa4d6b43097ab884af78fd3f41fbed214a0449ac6e4822e4e5c320a9a45c11c3a55e7972aa42f6a1b11638f9955ed4d2ce932337487bdf973927b7caa4ff5fad05a1b1373cea5e57ae9742f6b8c55a5baeed0768202f9eae47b24de96b964484d21b5cef562f2cfd1b5",
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
                self._actual_decrypt, message, password.upper(), salt
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
