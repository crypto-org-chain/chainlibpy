# Copyright (c) 2020, hukkinj1 (licensed under the MIT License)
# Modifications Copyright (c) 2021-present, Crypto.org
# (licensed under the Apache License, Version 2.0)

from typing import List

from chainlibpy.generated.common import (
    CosmosSdkMsg,
    CosmosSdkTxInfo,
    HdWallet,
    MnemonicWordCount,
    Network,
    WalletCoin,
    build_signed_msg_tx,
)

DEFAULT_DERIVATION_PATH = "m/44'/394'/0'/0/0"
DEFAULT_BECH32_HRP = "cro"


class Wallet:
    def __init__(
        self, seed: str, path: str = DEFAULT_DERIVATION_PATH, hrp: str = DEFAULT_BECH32_HRP
    ):
        self.path = path
        self.hrp = hrp
        self.wallet = HdWallet.recover_wallet(seed, password=None)

    @classmethod
    def new(cls, path: str = DEFAULT_DERIVATION_PATH, hrp: str = DEFAULT_BECH32_HRP) -> "Wallet":
        seed = HdWallet.generate_wallet(
            password=None, word_count=MnemonicWordCount.TWENTY_FOUR
        ).get_backup_mnemonic_phrase()
        return Wallet(seed, path, hrp)

    @property
    def private_key(self) -> bytes:
        """Get a private key from a mnemonic seed and a derivation path.

        Assumes a BIP39 mnemonic seed with no passphrase. Raises
        `chainlibpy.BIP32DerivationError` if the resulting private key
        is invalid.
        """
        return bytes(self.wallet.get_key(self.path).to_bytes())

    @property
    def public_key(self) -> bytes:
        return bytes(self.wallet.get_key(self.path).get_public_key_bytes())

    @property
    def address(self) -> str:
        if self.hrp == "cro":
            return self.wallet.get_default_address(
                WalletCoin.COSMOS_SDK(Network.CRYPTO_ORG_MAINNET())
            )
        else:
            return self.wallet.get_default_address(
                WalletCoin.COSMOS_SDK(Network.CRYPTO_ORG_TESTNET())
            )

    def sign_tx(self, tx_info: CosmosSdkTxInfo, msgs: List[CosmosSdkMsg]) -> bytes:
        """Constructs and signs the transaction with wallet's private key.

        Args:
            tx_info (CosmosSdkTxInfo): transaction information,
            msgs (List[CosmosSdkMsg]): messages to be included in the transactions
        Returns:
            bytes: the signed transaction payload bytes
        """
        return bytes(build_signed_msg_tx(tx_info, msgs, self.wallet.get_key(self.path)))
