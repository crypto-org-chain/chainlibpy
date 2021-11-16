from dataclasses import dataclass
PROTOBUF_PACKAGE = "cosmos.base.v1beta1"

@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class Coin:
  denom: str
  amount: str

BaseCoin = Coin(denom="", amount="")


