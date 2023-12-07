import os

from argon2 import PasswordHasher
from Crypto.Cipher import AES
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    mode = input("Encrypt or decrypt? ")

    if mode == "encrypt":
        msg = input("Message: ")
        password = input("Password: ")
        salt = input("Salt: ")

        ph = PasswordHasher()
        key = ph.hash(password, salt=salt.encode("utf-8"))

        cipher = AES.new(
            os.environ["ENCRYPTION_KEY"].encode("utf-8"),
            AES.MODE_EAX,
            nonce=key.encode("utf-8"),
        )
        encrypted_msg = cipher.encrypt(msg.encode("utf-8"))
        print(encrypted_msg.hex())
    else:
        msg = input("Message: ")
        password = input("Password: ")
        salt = input("Salt: ")

        ph = PasswordHasher()
        key = ph.hash(password, salt=salt.encode("utf-8"))

        cipher = AES.new(
            os.environ["ENCRYPTION_KEY"].encode("utf-8"),
            AES.MODE_EAX,
            nonce=key.encode("utf-8"),
        )
        decrypted_msg = cipher.decrypt(bytes.fromhex(msg))
        print(decrypted_msg)
