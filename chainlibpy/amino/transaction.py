import base64
import hashlib
import json
from typing import List

import ecdsa

from chainlibpy.amino import StdFee, StdSignDoc, SyncMode
from chainlibpy.amino.message import Msg
from chainlibpy.amino.tx import Pubkey, Signature, StdTx
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
            multi_sign_address: str = None,
    ) -> None:
        self._multi_sign_address = multi_sign_address
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
        std_tx = StdTx(self._msgs, self._fee, self._memo, self._timeout_height, [self.signature])

        pushable_tx = {
            "tx": std_tx.to_dict(),
            "mode": self._sync_mode,
        }
        return pushable_tx

    @property
    def signature(self) -> Signature:
        pubkey = self._wallet.public_key
        base64_pubkey = base64.b64encode(pubkey).decode("utf-8")
        pubkey = Pubkey(value=base64_pubkey)
        signature = Signature(self._sign(), pubkey, self._account_num, self._sequence)
        return signature

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

        print(list(signature_compact))
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