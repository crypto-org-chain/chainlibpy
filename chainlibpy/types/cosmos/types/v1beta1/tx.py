from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union, Literal
from chainlibpy.types.cosmos.crypto.multisign.v1beta1.multisign import CompactBitArray
from chainlibpy.types.cosmos.base.b1beta1.coin import Coin
from chainlibpy.generated.google.protobuf.any_pb2 import Any
from chainlibpy.transaction.msg.cosmos_msg import CosmosMsg

PROTOBUF_PACKAGE = "cosmos.tx.v1beta1"

SIGN_MODE_UNSPECIFIED = 0
SIGN_MODE_DIRECT = 1
SIGN_MODE_TEXTUAL = 2
SIGN_MODE_LEGACY_AMINO_JSON = 127
UNRECOGNIZED = -1

SIGN_MODE = Literal[SIGN_MODE_UNSPECIFIED, SIGN_MODE_DIRECT, SIGN_MODE_TEXTUAL, SIGN_MODE_LEGACY_AMINO_JSON, UNRECOGNIZED]

@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class TxBody:
    messages: List[CosmosMsg]
    memo: str
    timeout_height: int
    extension_options: List[Any]
    non_critical_extension_options: List[Any]

@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class ModeInfoSingle:
    mode: SIGN_MODE

@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class ModeInfoMulti:
    bitarray: Optional[CompactBitArray]
    modeInfos: Union[ModeInfoSingle, ModeInfoMulti]


@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class SignerInfo:
    public_key: Optional[Any]
    modeInfo: Union[ModeInfoSingle, ModeInfoMulti]
    sequence: int

@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class Fee:
    amount: List[Coin]
    gasLimit: int


@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class AuthInfo:
    signerInfos: List[SignerInfo]
    fee: Optional[Fee]

@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class Tx:
    boxy: TxBody
    authInfo: AuthInfo
    signatures: bytes

@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class TxRaw:
    body_bytes: bytes
    auth_info_bytes: bytes
    signatures: List[bytes]

@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class SignDoc:
    body_bytes: bytes
    auth_info_bytes: bytes
    chain_id: str
    account_number: int
