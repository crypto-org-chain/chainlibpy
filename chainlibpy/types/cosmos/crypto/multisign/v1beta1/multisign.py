from dataclasses import dataclass

PROTOBUF_PACKAGE = "cosmos.crypto.multisig.v1beta1"

@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class CompactBitArray:
    pass