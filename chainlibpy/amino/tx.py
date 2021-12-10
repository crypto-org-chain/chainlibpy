from dataclasses import dataclass
from typing import List

from .basic import BasicObj, StdFee
from .message import Msg


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class Pubkey(BasicObj):
    value: str

    def to_dict(self):
        return {"type": "tendermint/PubKeySecp256k1", "value": self.value}


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class Signature(BasicObj):
    signature: str
    pub_key: Pubkey
    account_number: str
    sequence: str

    def to_dict(self):
        return {
            "signature": self.signature,
            "pub_key": self.pub_key.to_dict(),
            "account_number": self.account_number,
            "sequence": self.sequence,
        }


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class StdTx(BasicObj):
    msg: List[Msg]
    fee: StdFee
    memo: str
    timeout_height: str
    signatures: List[Signature]

    def to_dict(self):
        return {
            "msg": [m.to_dict() for m in self.msg],
            "fee": self.fee.to_dict(),
            "memo": self.memo,
            "timeout_height": self.timeout_height,
            "signatures": [s.to_dict() for s in self.signatures],
        }
