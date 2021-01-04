# Copyright (c) 2020, hukkinj1 (licensed under the MIT License)
# Modifications Copyright (c) 2020, Foris Limited (licensed under the Apache License, Version 2.0)

import base64
import hashlib
import json
import sys
from typing import Any, Dict, List

import ecdsa

from chainlibpy._wallet import Wallet

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


# Valid transaction broadcast modes for the `POST /txs` endpoint of the
# Crypto.com REST API.
SyncMode = Literal["sync", "async", "block"]
DEFAULT_BECH32_HRP_BASE = "basecro"


class Transaction:
    """A Cosmos transaction.

    After initialization, one or more token transfers can be added by
    calling the `add_transfer()` method. Finally, call `get_pushable()`
    to get a signed transaction that can be pushed to the `POST /txs`
    endpoint of the Cosmos REST API.
    """

    def __init__(
        self,
        *,
        wallet: Wallet,
        account_num: int,
        sequence: int,
        fee: int = 0,
        gas: int = 200000,
        fee_denom: str = "basecro",
        memo: str = "",
        chain_id: str = "crypto-crocncl-1",
        sync_mode: SyncMode = "sync",
    ) -> None:
        self._wallet = wallet
        self._account_num = account_num
        self._sequence = sequence
        self._fee = fee
        self._fee_denom = fee_denom
        self._gas = gas
        self._memo = memo
        self._chain_id = chain_id
        self._sync_mode = sync_mode
        self._msgs: List[dict] = []

    def add_transfer(
        self, to_address: str, amount: int, base_denom: str = DEFAULT_BECH32_HRP_BASE
    ) -> None:
        transfer = {
            "type": "cosmos-sdk/MsgSend",
            "value": {
                "from_address": self._wallet.address,
                "to_address": to_address,
                "amount": [{"denom": base_denom, "amount": str(amount)}],
            },
        }
        self._msgs.append(transfer)

    def get_pushable(self) -> dict:
        """get the request post to the /txs."""
        pubkey = self._wallet.public_key
        base64_pubkey = base64.b64encode(pubkey).decode("utf-8")
        pushable_tx = {
            "tx": {
                "msg": self._msgs,
                "fee": {
                    "gas": str(self._gas),
                    "amount": [{"amount": str(self._fee), "denom": self._fee_denom}],
                },
                "memo": self._memo,
                "signatures": [
                    {
                        "signature": self._sign(),
                        "pub_key": {
                            "type": "tendermint/PubKeySecp256k1",
                            "value": base64_pubkey,
                        },
                        "account_number": str(self._account_num),
                        "sequence": str(self._sequence),
                    }
                ],
            },
            "mode": self._sync_mode,
        }
        return pushable_tx

    def _sign(self) -> str:
        message_str = json.dumps(
            self._get_sign_message(), separators=(",", ":"), sort_keys=True
        )
        message_bytes = message_str.encode("utf-8")

        privkey = ecdsa.SigningKey.from_string(
            self._wallet.private_key, curve=ecdsa.SECP256k1
        )
        signature_compact = privkey.sign_deterministic(
            message_bytes,
            hashfunc=hashlib.sha256,
            sigencode=ecdsa.util.sigencode_string_canonize,
        )

        signature_base64_str = base64.b64encode(signature_compact).decode("utf-8")
        return signature_base64_str

    def _get_sign_message(self) -> Dict[str, Any]:
        result = {
            "account_number": str(self._account_num),
            "sequence": str(self._sequence),
            "chain_id": self._chain_id,
            "memo": self._memo,
            "fee": {
                "gas": str(self._gas),
                "amount": [{"amount": str(self._fee), "denom": self._fee_denom}],
            },
            "msgs": self._msgs,
        }
        return result
