import base64

from chainlibpy.amino.basic import BasicObj
from chainlibpy.generated.cosmos.crypto.multisig.v1beta1.multisig_pb2 import (
    CompactBitArray as ProtoCompactBitArray,
)
from chainlibpy.multisign.bits import Bits


class CompactBitArray(BasicObj):
    MaxInt32 = 2147483647

    def __init__(self, bits: int):
        self.extra_bits_stored = 0
        self.elems = bytearray()
        if bits <= 0:
            raise Exception(f"invalid bits {bits}")
        n_elems = (bits + 7) // 8
        if n_elems <= 0 or n_elems > self.MaxInt32:
            raise Exception(f"invalid bits {bits}")
        self.extra_bits_stored = bits % 8
        self.elems = bytearray([0] * n_elems)

    def __repr__(self):
        elems = base64.b64encode(self.elems).decode('utf-8')
        return f"extra_bits_stored:{self.extra_bits_stored}, elems:{elems}"

    def bit_array(self) -> ProtoCompactBitArray:
        return ProtoCompactBitArray(
            extra_bits_stored=self.extra_bits_stored,
            elems=bytes(self.elems)
        )

    def count(self) -> int:
        """returns the number of bits in the bitarray."""
        if self.extra_bits_stored == 0:
            return len(self.elems) * 8
        return (len(self.elems) - 1) * 8 + int(self.extra_bits_stored)

    def get_index(self, index: int) -> bool:
        """returns the bit at index i within the bit array.

        The behavior is undefined if i >= self.count()
        """
        if index < 0 or index >= self.count():
            return False
        return (self.elems[index >> 3] & (1 << (7 - (index % 8)))) > 0

    def set_index(self, i: int, v: bool) -> bool:
        """set_index sets the bit at index i within the bit array.

        Returns true if and only if the operation succeeded. The
        behavior is undefined if i >= self.count()
        """
        if i < 0 or i >= self.count():
            return False

        if v:
            self.elems[i >> 3] |= (1 << (7 - (i % 8)))
        else:
            self.elems[i >> 3] &= ~(1 << (7 - (i % 8)))
        return True

    def num_true_bits_before(self, index: int) -> int:
        ones_count = 0
        max_ = self.count()
        index = min(index, max_)
        elem = 0
        while True:
            if elem*8+7 >= index:
                ones_count += Bits.ones_count8(self.elems[elem]) >> (7 - (index % 8) + 1)
                return ones_count
            ones_count += Bits.ones_count8(self.elems[elem])
            elem += 1
