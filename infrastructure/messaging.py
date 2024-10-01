from cryptography.fernet import Fernet

ENCODING: str = 'utf-8'

class MessageService:
    def __init__(self, cipher: Fernet) -> None:
        self._cipher = cipher

    def encrypt(self, message: str) -> bytes:
        message_bytes = message.encode(ENCODING)
        return self._cipher.encrypt(message_bytes)

    def decrypt(self, encrypted_message: bytes) -> str:
        decrypted_message_bytes = self._cipher.decrypt(encrypted_message)
        return decrypted_message_bytes.decode(ENCODING)