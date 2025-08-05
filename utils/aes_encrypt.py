from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json

key_raw = b"WraithDropAESKey!"  # 16 bytes key (exact length, no encode needed)
KEY = key_raw[:16]

print(f"[DEBUG] AES KEY length: {len(KEY)} bytes")

def pad(s):
    pad_len = AES.block_size - len(s) % AES.block_size
    return s + chr(pad_len) * pad_len

def unpad(s):
    pad_len = ord(s[-1])
    return s[:-pad_len]

def encrypt(data: dict) -> str:
    raw = pad(json.dumps(data)).encode()
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(raw)
    return base64.b64encode(iv + encrypted).decode()

def decrypt(ciphertext: str) -> dict:
    data = base64.b64decode(ciphertext)
    iv = data[:16]
    encrypted = data[16:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted)
    return json.loads(unpad(decrypted.decode()))

