"""
Módulo de Análisis de Semillas BIP39 y Derivación de Claves.
"""

from typing import Dict, List
from bip_utils import (
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
    Bip39Languages,
    Bip44,
    Bip49,
    Bip84,
    Bip86,
    Bip44Coins,
    Bip44Changes
)


class KeyManager:
    def __init__(self, mnemonic: str, passphrase: str = ""):
        self.mnemonic = mnemonic.strip().lower()
        self.passphrase = passphrase

        if not self.validate_mnemonic(self.mnemonic):
            raise ValueError("Error: La frase mnemónica BIP39 provista no es válida.")

        self.seed = Bip39SeedGenerator(self.mnemonic).Generate(self.passphrase)

    @staticmethod
    def validate_mnemonic(mnemonic: str) -> bool:
        try:
            return Bip39MnemonicValidator(Bip39Languages.ENGLISH).IsValid(mnemonic)
        except Exception:
            return False

    def derive_bip84_native_segwit(self, account: int = 0, change: bool = False, index: int = 0) -> Dict[str, str]:
        bip84_mst = Bip84.FromSeed(self.seed, Bip44Coins.BITCOIN)
        bip84_acc = bip84_mst.Purpose().Coin().Account(account)
        chg = Bip44Changes.CHAIN_INT if change else Bip44Changes.CHAIN_EXT
        addr_obj = bip84_acc.Change(chg).AddressIndex(index)

        return {
            "standard": "BIP84 (Native SegWit)",
            "path": f"m/84'/0'/{account}'/{1 if change else 0}/{index}",
            "address": addr_obj.PublicKey().ToAddress(),
            "wif": addr_obj.PrivateKey().ToWif(),
            "pubkey": addr_obj.PublicKey().RawCompressed().ToHex(),
            "extended_pubkey": bip84_acc.PublicKey().ToExtended()
        }

    def derive_bip86_taproot(self, account: int = 0, change: bool = False, index: int = 0) -> Dict[str, str]:
        bip86_mst = Bip86.FromSeed(self.seed, Bip44Coins.BITCOIN)
        bip86_acc = bip86_mst.Purpose().Coin().Account(account)
        chg = Bip44Changes.CHAIN_INT if change else Bip44Changes.CHAIN_EXT
        addr_obj = bip86_acc.Change(chg).AddressIndex(index)

        return {
            "standard": "BIP86 (Taproot)",
            "path": f"m/86'/0'/{account}'/{1 if change else 0}/{index}",
            "address": addr_obj.PublicKey().ToAddress(),
            "wif": addr_obj.PrivateKey().ToWif(),
            "pubkey": addr_obj.PublicKey().RawCompressed().ToHex(),
            "extended_pubkey": bip86_acc.PublicKey().ToExtended()
        }

    def derive_bip49_nested_segwit(self, account: int = 0, change: bool = False, index: int = 0) -> Dict[str, str]:
        bip49_mst = Bip49.FromSeed(self.seed, Bip44Coins.BITCOIN)
        bip49_acc = bip49_mst.Purpose().Coin().Account(account)
        chg = Bip44Changes.CHAIN_INT if change else Bip44Changes.CHAIN_EXT
        addr_obj = bip49_acc.Change(chg).AddressIndex(index)

        return {
            "standard": "BIP49 (Nested SegWit)",
            "path": f"m/49'/0'/{account}'/{1 if change else 0}/{index}",
            "address": addr_obj.PublicKey().ToAddress(),
            "wif": addr_obj.PrivateKey().ToWif(),
            "pubkey": addr_obj.PublicKey().RawCompressed().ToHex(),
            "extended_pubkey": bip49_acc.PublicKey().ToExtended()
        }

    def derive_bip44_legacy(self, account: int = 0, change: bool = False, index: int = 0) -> Dict[str, str]:
        bip44_mst = Bip44.FromSeed(self.seed, Bip44Coins.BITCOIN)
        bip44_acc = bip44_mst.Purpose().Coin().Account(account)
        chg = Bip44Changes.CHAIN_INT if change else Bip44Changes.CHAIN_EXT
        addr_obj = bip44_acc.Change(chg).AddressIndex(index)

        return {
            "standard": "BIP44 (Legacy)",
            "path": f"m/44'/0'/{account}'/{1 if change else 0}/{index}",
            "address": addr_obj.PublicKey().ToAddress(),
            "wif": addr_obj.PrivateKey().ToWif(),
            "pubkey": addr_obj.PublicKey().RawCompressed().ToHex(),
            "extended_pubkey": bip44_acc.PublicKey().ToExtended()
        }

    def scan_derivation_matrix(self, max_index: int = 5) -> List[Dict[str, str]]:
        matrix = []
        for i in range(max_index):
            matrix.append(self.derive_bip84_native_segwit(index=i))
            matrix.append(self.derive_bip86_taproot(index=i))
            matrix.append(self.derive_bip49_nested_segwit(index=i))
            matrix.append(self.derive_bip44_legacy(index=i))
        return matrix
