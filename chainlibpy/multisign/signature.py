import base64
from dataclasses import dataclass
from typing import List

from chainlibpy.generated.cosmos.tx.v1beta1.tx_pb2 import SignerInfo, ModeInfo

from chainlibpy.generated.cosmos.crypto.multisig.keys_pb2 import LegacyAminoPubKey
from google.protobuf.any_pb2 import Any as ProtoAny

from chainlibpy.amino.basic import BasicObj
from chainlibpy.generated.cosmos.crypto.multisig.v1beta1.multisig_pb2 import (
    CompactBitArray as ProtoCompactBitArray,
)
from chainlibpy.generated.cosmos.crypto.secp256k1.keys_pb2 import PubKey as ProtoPubKey
from chainlibpy.generated.cosmos.tx.signing.v1beta1.signing_pb2 import SignMode
from chainlibpy.multisign.bitarray import CompactBitArray


def packed_to_any(m):
    packed = ProtoAny()
    packed.Pack(m, type_url_prefix="/")
    return packed


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class SingleSignatureData(BasicObj):
    sign_mode: SignMode
    signature: bytes


class SingleSignatureV2(object):
    pub_key: ProtoPubKey
    data: SingleSignatureData
    sequence: int

    def __init__(self, pub_key: bytes, sequence: int, raw_sig: bytes):
        self.pub_key = ProtoPubKey(key=pub_key)
        self.data = SingleSignatureData(
            sign_mode=SignMode.SIGN_MODE_LEGACY_AMINO_JSON,
            signature=raw_sig
        )
        self.sequence = sequence


class MultiSignatureData(object):
    def __init__(self, n: int):
        self._bit_array = CompactBitArray(n)
        self.signatures = []

    def __repr__(self):
        signatures = [base64.b64encode(s).decode('utf-8') for s in self.signatures]
        return f"signatures: {signatures}, bit_array: {self.bit_array}"

    @property
    def bit_array(self) -> ProtoCompactBitArray:
        return self._bit_array.bit_array()

    def add_signature_from_pubkey(
            self,
            sig: bytes,
            pubkey: ProtoPubKey,
            all_pubkeys: List[ProtoPubKey]
    ):
        index = all_pubkeys.index(packed_to_any(pubkey))
        new_sig_index = self._bit_array.num_true_bits_before(index)

        # replace the old
        if self._bit_array.get_index(index):
            self.signatures[new_sig_index] = sig
            return
        self._bit_array.set_index(index, True)

        # Optimization if the index is the greatest index
        if new_sig_index == len(self.signatures):
            self.signatures.append(sig)
            return

        # insert at the new_sig_index
        self.signatures.insert(new_sig_index, sig)

    def add_single_sig_v2(
            self,
            single_sig_v2: SingleSignatureV2,
            all_pubkeys: List[ProtoPubKey]
    ):
        self.add_signature_from_pubkey(
            single_sig_v2.data.signature,
            single_sig_v2.pub_key,
            all_pubkeys
        )


def gen_packed_send_msg(
    sequence: int,
    multi_pubkey: LegacyAminoPubKey,
    bitarray: ProtoCompactBitArray
) -> SignerInfo:
    multi_pubkey_packed = ProtoAny()
    multi_pubkey_packed.Pack(multi_pubkey, type_url_prefix="/")

    # Prepare auth info
    signal_mode_info = ModeInfo(single=ModeInfo.Single(mode=SignMode.SIGN_MODE_LEGACY_AMINO_JSON))
    mode_infos = [signal_mode_info] * multi_pubkey.threshold
    multi = ModeInfo.Multi(bitarray=bitarray, mode_infos=mode_infos)
    mode_info = ModeInfo(multi=multi)
    signer_info = SignerInfo(
        public_key=multi_pubkey_packed,
        mode_info=mode_info,
        sequence=sequence,
    )
    return signer_info
