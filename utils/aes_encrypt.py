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
    print(f"[DEBUG] Raw to encrypt: {raw}")
    iv = get_random_bytes(16)
    print(f"[DEBUG] IV: {iv.hex()}")
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(raw)
    print(f"[DEBUG] Encrypted bytes: {encrypted.hex()}")
    out = base64.b64encode(iv + encrypted).decode()
    print(f"[DEBUG] Base64 output: {out}")
    return out

def decrypt(ciphertext: str) -> dict:
    print(f"[DEBUG] Ciphertext input: {ciphertext}")
    data = base64.b64decode(ciphertext)
    iv = data[:16]
    print(f"[DEBUG] IV: {iv.hex()}")
    encrypted = data[16:]
    print(f"[DEBUG] Encrypted bytes: {encrypted.hex()}")
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted)
    print(f"[DEBUG] Decrypted bytes: {decrypted}")
    json_data = unpad(decrypted.decode())
    print(f"[DEBUG] Unpadded: {json_data}")
    return json.loads(json_data)

if __name__ == "__main__":
    test_data = {"foo": "bar"}
    ct = encrypt(test_data)
    print(f"[DEBUG] Encrypted: {ct}")
    pt = decrypt(ct)
    print(f"[DEBUG] Decrypted: {pt}")
