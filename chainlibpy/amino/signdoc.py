from dataclasses import dataclass
from typing import List

from .basic import StdFee
from .message import Msg, to_dict


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class StdSignDoc:
    chain_id: str
    account_number: str
    sequence: str
    fee: StdFee
    msgs: List[Msg]
    memo: str
    timeout_height: str

    def to_dict(self):
        data = {
            "account_number": self.account_number,
            "sequence": self.sequence,
            "chain_id": self.chain_id,
            "memo": self.memo,
            "fee": to_dict(self.fee),
            "msgs": [m.to_dict() for m in self.msgs],
        }
        if self.timeout_height != "0":
            data["timeout_height"] = self.timeout_height
        return data
