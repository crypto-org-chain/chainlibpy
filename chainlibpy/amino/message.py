import hashlib
import json
from dataclasses import dataclass
from typing import List

from .basic import (
    Coin,
    CommissionRates,
    Content,
    Description,
    Input,
    Output,
    TimeoutHeight,
    VoteOption,
    to_dict,
)


class Msg:
    @property
    def msg_type(self):
        return f"cosmos-sdk/{self.__class__.__name__}"

    def to_dict(self) -> dict:
        return {
            "type": self.msg_type,
            "value": to_dict(self),
        }


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgSend(Msg):
    """A high level transaction of the coin module."""

    # Bech32 account address
    from_address: str
    # Bech32 account address
    to_address: str
    amount: List[Coin]


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgMultiSend(Msg):
    """A high level transaction of the coin module."""

    inputs: List[Input]
    outputs: List[Output]


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgVerifyInvariant(Msg):
    """Verifies a particular invariance.

    see https://github.com/cosmos/cosmos-sdk/blob/efa73c7/proto/cosmos/crisis/crisis.proto.
    """

    sender: str
    invariant_module_name: str
    invariant_route: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgSetWithdrawAddress(Msg):
    """Message for delegation withdraw from a single validator."""

    # Bech32 account address
    delegator_address: str
    # Bech32 account address
    withdraw_address: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgWithdrawDelegationReward(Msg):
    """Changes the withdraw address for a delegator (or validator self-
    delegation)"""

    # Bech32 account address
    delegator_address: str
    # Bech32 account address
    validator_address: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgWithdrawValidatorCommission(Msg):
    """Message for validator withdraw."""

    # Bech32 account address
    validator_address: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgFundCommunityPool(Msg):
    """Allows an account to directly fund the community pool."""

    amount: List[Coin]
    # Bech32 account address
    depositor: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgSubmitEvidence(Msg):
    """Supports submitting arbitrary evidence."""

    # Bech32 account address
    submitter: str
    evidence: Content


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgSubmitProposal(Msg):
    """Supports submitting arbitrary proposal content."""

    content: Content
    initial_deposit: List[Coin]
    # Bech32 account address
    proposer: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgVote(Msg):
    """Casts a vote."""

    proposal_id: int
    # Bech32 account address
    voter: str
    option: VoteOption


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgDeposit(Msg):
    """Submits a deposit to an existing proposal."""

    proposal_id: int
    # Bech32 account address
    depositor: str
    amount: List[Coin]


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgUnjail(Msg):
    """Unjails a jailed validator."""

    # Bech32 account address
    validator_addr: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgCreateValidator(Msg):
    """Creates a new validator."""

    description: Description
    commission: CommissionRates
    min_self_delegation: str
    # Bech32 encoded delegator address
    delegator_address: str
    # Bech32 encoded validator address
    validator_address: str
    # Bech32 encoded public key
    pubkey: str
    value: Coin


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgEditValidator(Msg):
    """Edits an existing validator."""

    description: Description
    # Bech32 encoded validator address
    validator_address: str
    commission_rate: str
    min_self_delegation: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgDelegate(Msg):
    """Performs a delegation from a delegate to a validator.

    see https://docs.cosmos.network/master/modules/staking/03_messages.html#msgdelegate
    """

    # Bech32 encoded delegator address
    delegator_address: str
    #  Bech32 encoded validator address
    validator_address: str
    amount: Coin


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgBeginRedelegate(Msg):
    """Performs a redelegation from a delegate and source validator to a
    destination validator."""

    # Bech32 encoded delegator address
    delegator_address: str
    # Bech32 encoded source validator address
    validator_src_address: str
    # Bech32 encoded destination validator address
    validator_dst_address: str
    amount: Coin


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgUndelegate(Msg):
    """Performs an undelegation from a delegate and a validator."""

    # Bech32 encoded delegator address
    delegator_address: str
    # Bech32 encoded validator address
    validator_address: str
    amount: Coin


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class IbcMsgTransfer(Msg):
    source_port: str
    source_channel: str
    sender: str
    receiver: str
    coin: Coin
    packet_timeout_height: TimeoutHeight = TimeoutHeight()
    packet_timeout_timestamp: str = "0"
    absolute_timeouts: bool = True

    def fix_coin_denom(self):
        raw_denom = self.coin.denom
        if raw_denom.startswith("ibc/"):
            return
        else:
            denom_split = raw_denom.split("/")
            if denom_split[0] == raw_denom:
                denom_trace = {
                    "path": "",
                    "base_denom": raw_denom,
                }
            else:
                denom_trace = {
                    "path": "/".join(denom_split[0:-1]),
                    "base_denom": denom_split[-1],
                }
            # return 'ibc/{hash(tracePath + baseDenom)}'
            # If the trace is empty, it will return the base denomination.
            if denom_trace["path"] != "":
                self.coin.denom = "ibc/{}".format(self.get_full_denom_path_checksum(denom_trace))
            else:
                self.coin.denom = denom_trace["base_denom"]

    @classmethod
    def get_full_denom_path_checksum(cls, denom_trace):
        if denom_trace["path"] != "":
            data = "{}/{}".format(denom_trace["path"], denom_trace["base_denom"])
        else:
            data = denom_trace["base_denom"]
        return hashlib.sha256(data.encode()).hexdigest().upper()

    def to_dict(self) -> dict:
        self.fix_coin_denom()
        data = {
            "type": "cosmos-sdk/MsgTransfer",
            "value": {
                "receiver": self.receiver,
                "sender": self.sender,
                "source_channel": self.source_channel,
                "source_port": self.source_port,
                "token": self.coin.to_dict(),
            },
        }
        timeout_height = self.packet_timeout_height.to_dict()
        if timeout_height:
            data["value"]["timeout_height"] = timeout_height
        if self.packet_timeout_timestamp != "0":
            data["value"]["timeout_timestamp"] = self.packet_timeout_timestamp
        return data


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgNFT(Msg):
    @property
    def msg_type(self):
        return f"chainmain/nft/{self.__class__.__name__}"


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgIssueDenom(MsgNFT):
    id: str
    name: str
    schema: dict
    sender: str

    def to_dict(self) -> dict:
        schema = json.dumps(self.schema, separators=(",", ":"))
        data = {
            "type": self.msg_type,
            "value": {
                "id": self.id,
                "name": self.name,
                "schema": schema,
                "sender": self.sender,
            },
        }
        return data


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgTransferNFT(MsgNFT):
    id: str
    denom_id: str
    sender: str
    recipient: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgEditNFT(MsgNFT):
    id: str
    denom_id: str
    name: str
    uri: str
    data: str
    sender: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgMintNFT(MsgNFT):
    id: str
    denom_id: str
    name: str
    uri: str
    data: str
    sender: str
    recipient: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class MsgBurnNFT(MsgNFT):
    id: str
    denom_id: str
    sender: str


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class BaseNFT(MsgNFT):
    id: str
    name: str
    uri: str
    data: str
    owner: str
