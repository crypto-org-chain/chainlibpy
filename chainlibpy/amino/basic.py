import sys
from dataclasses import dataclass
from typing import List

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

# Valid transaction broadcast modes for the `POST /txs` endpoint of the
# Crypto.org Chain REST API.
SyncMode = Literal["sync", "async", "block"]
DEFAULT_BECH32_HRP_BASE = "basecro"

VoteOptionUnspecified = 0
VoteOptionYes = 1
VoteOptionAbstain = 2
VoteOptionNo = 3
VoteOptionNoWithVeto = 4

VoteOption = Literal[
    VoteOptionUnspecified,
    VoteOptionYes,
    VoteOptionAbstain,
    VoteOptionNo,
    VoteOptionNoWithVeto,
]


def to_dict(obj):
    if isinstance(obj, (str, bytes, int)) or not obj:
        return obj
    if not isinstance(obj, (dict, list)):
        return to_dict(vars(obj))
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = to_dict(v)
    elif isinstance(obj, list):
        obj = [to_dict(i) for i in obj]
    return obj


class BasicObj:
    def to_dict(self):
        return to_dict(self)


@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class Coin(BasicObj):
    amount: str = "0"
    denom: str = DEFAULT_BECH32_HRP_BASE


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class TimeoutHeight(BasicObj):
    revision_number: str = "0"
    revision_height: str = "0"

    def to_dict(self):
        data = {}
        if self.revision_number != "0":
            data["revision_number"] = self.revision_number
        if self.revision_height != "0":
            data["revision_height"] = self.revision_height
        return data


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class StdFee(BasicObj):
    gas: str
    amount: List[Coin]

    @classmethod
    def default(cls):
        return cls("200000", [])


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class Input(BasicObj):
    # Bech32 account address
    address: str
    coins: List[Coin]


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class Output(BasicObj):
    # Bech32 account address
    address: str
    coins: List[Coin]


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class Content(BasicObj):
    type_url: str
    value: bytes


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class CommissionRates(BasicObj):
    """The initial commission rates to be used for creating a validator."""

    rate: str
    max_rate: str
    max_change_rate: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class Description(BasicObj):
    """A validator description."""

    moniker: str
    identity: str
    website: str
    security_contact: str
    details: str
