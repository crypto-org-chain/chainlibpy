# Copyright (c) 2020, hukkinj1 (licensed under the MIT License)
# Modifications Copyright (c) 2020, Foris Limited (licensed under the Apache License, Version 2.0)

import hashlib

import bech32
import ecdsa
import hdwallets
from mnemonic import Mnemonic

DEFAULT_DERIVATION_PATH = "m/44'/394'/0'/0/0"
DEFAULT_BECH32_HRP = "cro"


class Wallet:
    def __init__(self, seed: str, path=DEFAULT_DERIVATION_PATH, hrp=DEFAULT_BECH32_HRP):
        self.seed = seed
        self.path = path
        self.hrp = hrp

    @classmethod
    def new(cls, path=DEFAULT_DERIVATION_PATH, hrp=DEFAULT_BECH32_HRP):
        seed = Mnemonic(language="english").generate(strength=256)
        return Wallet(seed, path, hrp)

    @property
    def private_key(self) -> bytes:
        """Get a private key from a mnemonic seed and a derivation path.

        Assumes a BIP39 mnemonic seed with no passphrase. Raises
        `chainlibpy.BIP32DerivationError` if the resulting private key
        is invalid.
        """
        seed_bytes = Mnemonic.to_seed(self.seed, passphrase="")
        hd_wallet = hdwallets.BIP32.from_seed(seed_bytes)
        # This can raise a `hdwallets.BIP32DerivationError` (which we alias so
        # that the same exception type is also in the `chainlibpy` namespace).
        derived_privkey = hd_wallet.get_privkey_from_path(self.path)

        return derived_privkey

    @property
    def public_key(self) -> bytes:
        privkey_obj = ecdsa.SigningKey.from_string(self.private_key, curve=ecdsa.SECP256k1)
        pubkey_obj = privkey_obj.get_verifying_key()
        return pubkey_obj.to_string("compressed")

    @property
    def address(self) -> str:
        s = hashlib.new("sha256", self.public_key).digest()
        r = hashlib.new("ripemd160", s).digest()
        five_bit_r = bech32.convertbits(r, 8, 5)
        assert five_bit_r is not None, "Unsuccessful bech32.convertbits call"
        return bech32.bech32_encode(self.hrp, five_bit_r)
