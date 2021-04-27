# Copyright (c) 2020, hukkinj1 (licensed under the MIT License)
# Modifications Copyright (c) 2020, Foris Limited (licensed under the Apache License, Version 2.0)

import base64
import hashlib
import json
from typing import List

import ecdsa

from chainlibpy.amino import StdFee, StdSignDoc, SyncMode
from chainlibpy.amino.message import Msg
from chainlibpy.wallet import Wallet


class Transaction:
    """A Cosmos transaction.

    After initialization, one or more token transfers can be added by
    calling the `add_transfer()` method. Finally, call `get_pushable()`
    to get a signed transaction that can be pushed to the `POST /txs`
    endpoint of the Cosmos REST API.
    """

    def __init__(
        self,
        wallet: Wallet,
        account_num: int,
        sequence: int,
        fee: StdFee = StdFee.default(),
        memo: str = "",
        chain_id: str = "crypto-org-chain-mainnet-1",
        sync_mode: SyncMode = "sync",
        timeout_height: int = 0,
    ) -> None:
        self._wallet = wallet
        self._account_num = str(account_num)
        self._sequence = str(sequence)
        self._fee = fee
        self._memo = memo
        self._chain_id = chain_id
        self._sync_mode = sync_mode
        self._msgs: List[Msg] = []
        self._timeout_height = str(timeout_height)

    def add_msg(self, msg: Msg):
        self._msgs.append(msg)

    def get_pushable(self) -> dict:
        """get the request post to the /txs."""
        pubkey = self._wallet.public_key
        base64_pubkey = base64.b64encode(pubkey).decode("utf-8")
        pushable_tx = {
            "tx": {
                "msg": [m.to_dict() for m in self._msgs],
                "fee": self._fee.to_dict(),
                "memo": self._memo,
                "timeout_height": self._timeout_height,
                "signatures": [
                    {
                        "signature": self._sign(),
                        "pub_key": {
                            "type": "tendermint/PubKeySecp256k1",
                            "value": base64_pubkey,
                        },
                        "account_number": self._account_num,
                        "sequence": self._sequence,
                    }
                ],
            },
            "mode": self._sync_mode,
        }
        return pushable_tx

    def _sign(self) -> str:
        sign_doc = self._get_sign_doc()
        message_str = json.dumps(
            sign_doc.to_dict(), separators=(",", ":"), sort_keys=True
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

    def _get_sign_doc(self) -> StdSignDoc:
        sign_doc = StdSignDoc(
            account_number=self._account_num,
            sequence=self._sequence,
            chain_id=self._chain_id,
            memo=self._memo,
            fee=self._fee.to_dict(),
            msgs=self._msgs,
            timeout_height=self._timeout_height,
        )
        return sign_doc
