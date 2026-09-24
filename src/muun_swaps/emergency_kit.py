"""
Módulo de Decodificación y Extracción de Claves de Kits de Emergencia (Muun Wallet).
"""

import json
import base64
from typing import Dict, Any
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class MuunEmergencyKitDecoder:
    def __init__(self, kit_json_content: str):
        try:
            self.data = json.loads(kit_json_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al analizar la estructura JSON del Kit: {e}")

    @staticmethod
    def derive_encryption_key(passphrase: str, salt_b64: str) -> bytes:
        salt = base64.b64decode(salt_b64)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=150000,
        )
        return kdf.derive(passphrase.encode('utf-8'))

    def decrypt_encrypted_key(self, encrypted_payload_b64: str, recovery_code: str, salt_b64: str) -> str:
        key = self.derive_encryption_key(recovery_code, salt_b64)
        payload = base64.b64decode(encrypted_payload_b64)

        nonce = payload[:12]
        ciphertext = payload[12:]

        aesgcm = AESGCM(key)
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_bytes.decode('utf-8')

    def parse_recovery_data(self, recovery_code: str = None) -> Dict[str, Any]:
        user_xpub = self.data.get("userKey", {}).get("xpub")
        muun_xpub = self.data.get("muunKey", {}).get("xpub")
        
        salt = self.data.get("userKey", {}).get("salt")
        encrypted_xpriv = self.data.get("userKey", {}).get("encryptedXpriv")

        decrypted_user_xpriv = None
        if recovery_code and encrypted_xpriv and salt:
            try:
                decrypted_user_xpriv = self.decrypt_encrypted_key(encrypted_xpriv, recovery_code, salt)
            except Exception as e:
                decrypted_user_xpriv = f"Error de descifrado: {e}"

        descriptors = {
            "p2wsh_multisig_descriptor": f"wsh(sortedmulti(2,{user_xpub}/<0;1>/*,{muun_xpub}/<0;1>/*))",
            "p2sh_p2wsh_multisig_descriptor": f"sh(wsh(sortedmulti(2,{user_xpub}/<0;1>/*,{muun_xpub}/<0;1>/*)))"
        }

        return {
            "version": self.data.get("version", "Desconocida"),
            "user_xpub": user_xpub,
            "muun_xpub": muun_xpub,
            "user_xpriv_decrypted": decrypted_user_xpriv,
            "descriptors": descriptors,
        }
