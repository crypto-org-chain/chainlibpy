import base64
import hashlib
import json
import sys
from typing import Any, Dict, List

import ecdsa

from cryptopy._wallet import DEFAULT_BECH32_HRP, DEFAULT_BECH32_HRP_BASE, Wallet

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


# Valid transaction broadcast modes for the `POST /txs` endpoint of the
# Cosmos REST API.
SyncMode = Literal["sync", "async", "block"]


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
        hrp: str = DEFAULT_BECH32_HRP,
        sync_mode: SyncMode = "sync",
        timeout_height: int = 0,
    ) -> None:
        self._wallet = wallet
        self._account_num = account_num
        self._sequence = sequence
        self._fee = fee
        self._fee_denom = fee_denom
        self._gas = gas
        self._memo = memo
        self._chain_id = chain_id
        self._hrp = hrp
        self._sync_mode = sync_mode
        self._timeout_height = timeout_height
        self._msgs: List[dict] = []

    def add_transfer(
        self, to_address: str, amount: int, denom: str = DEFAULT_BECH32_HRP_BASE
    ) -> None:
        transfer = {
            "type": "cosmos-sdk/MsgSend",
            "value": {
                "from_address": self._wallet.address,
                "to_address": to_address,
                "amount": [{"denom": denom, "amount": str(amount)}],
            },
        }
        self._msgs.append(transfer)

    def get_pushable(self) -> str:
        """
        get the request post to the /txs, https://cosmos.network/rpc/v0.37.9
        """
        if self._fee == 0:
            amount = [{"amount": str(self._fee), "denom": self._fee_denom}]
        else:
            amount = []
        pubkey = self._wallet.public_key
        base64_pubkey = base64.b64encode(pubkey).decode("utf-8")
        pushable_tx = {
            "tx": {
                "msg": self._msgs,
                "fee": {
                    "gas": str(self._gas),
                    "amount": amount,
                },
                "memo": self._memo,
                "signatures": [
                    {
                        "signature": self._sign(),
                        "pub_key": {"type": "tendermint/PubKeySecp256k1", "value": base64_pubkey},
                        "account_number": str(self._account_num),
                        "sequence": str(self._sequence),
                    }
                ],
            },
            "mode": self._sync_mode,
        }
        return json.dumps(pushable_tx, separators=(",", ":"))

    def _sign(self) -> str:
        message_str = json.dumps(self._get_sign_message(), separators=(",", ":"), sort_keys=True)
        print(message_str)
        message_bytes = message_str.encode("utf-8")
        print(message_bytes)

        privkey = ecdsa.SigningKey.from_string(self._wallet.private_key, curve=ecdsa.SECP256k1)
        signature_compact = privkey.sign_deterministic(
            message_bytes, hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_string_canonize
        )

        signature_base64_str = base64.b64encode(signature_compact).decode("utf-8")
        return signature_base64_str

    def _get_sign_message(self) -> Dict[str, Any]:
        if self._fee == 0:
            amount = []
        else:
            amount = [{"amount": str(self._fee), "denom": self._fee_denom}]

        result = {
            "account_number": str(self._account_num),
            "sequence": str(self._sequence),
            "chain_id": self._chain_id,
            "memo": self._memo,
            "fee": {
                "gas": str(self._gas),
                "amount": amount,
            },
            "msgs": self._msgs,
        }
        if self._timeout_height != 0:
            result["timeout_height"] = str(self._timeout_height)
        return result
