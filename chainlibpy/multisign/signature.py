import base64
from typing import List
from dataclasses import dataclass
from chainlibpy.amino.basic import BasicObj
from chainlibpy.multisign.bitarray import CompactBitArray
from chainlibpy.generated.cosmos.crypto.secp256k1.keys_pb2 import PubKey as ProtoPubKey
from chainlibpy.generated.cosmos.tx.signing.v1beta1.signing_pb2 import SignMode
from chainlibpy.generated.cosmos.crypto.multisig.v1beta1.multisig_pb2 import CompactBitArray as ProtoCompactBitArray


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
        self.data = SingleSignatureData(sign_mode=SignMode.SIGN_MODE_LEGACY_AMINO_JSON, signature=raw_sig)
        self.sequence = sequence


class MultiSignatureData(object):
    bit_array: CompactBitArray
    signatures: List[bytes]

    def __init__(self, n: int):
        self.bit_array = CompactBitArray(n)
        self.signatures = []

    def __repr__(self):
        signatures = [base64.b64encode(s).decode('utf-8') for s in self.signatures]
        return f"signatures: {signatures}, bit_array: {self.bit_array}"

    def bit_array(self) -> ProtoCompactBitArray:
        self.bit_array.bit_array()

    def add_signature_from_pubkey(self, sig: bytes, pubkey: ProtoPubKey, all_pubkeys: List[ProtoPubKey]):
        index = all_pubkeys.index(pubkey)
        new_sig_index = self.bit_array.num_true_bits_before(index)

        # replace the old
        if self.bit_array.get_index(index):
            self.signatures[new_sig_index] = sig
            return
        self.bit_array.set_index(index, True)

        # Optimization if the index is the greatest index
        if new_sig_index == len(self.signatures):
            self.signatures.append(sig)
            return

        # insert at the new_sig_index
        self.signatures.insert(new_sig_index, sig)
        # todo: remove this
        print([list(i) for i in self.signatures])

    def add_single_signature(self, single_sig_v2: SingleSignatureV2, all_pubkeys: List[ProtoPubKey]):
        self.add_signature_from_pubkey(single_sig_v2.data.signature, single_sig_v2.pub_key, all_pubkeys)
