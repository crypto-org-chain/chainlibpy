from dataclasses import dataclass
from typing import List

from .basic import (Coin, CommissionRates, Content, Description, Input, Output,
                    VoteOption, to_dict)


class Msg:
    def to_dict(self):
        return {
            "type": f"cosmos-sdk/{self.__class__.__name__}",
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
