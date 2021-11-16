from dataclasses import dataclass


@dataclass(init=True, repr=True, eq=True, order=True, frozen=False)
class Msg:
    type_url: str
    value: dict
