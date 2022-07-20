import decimal
from typing import Dict, Union

from chainlibpy.generated.common import SingleCoin
from chainlibpy.grpc_client import NetworkConfig

from .utils import is_integer

MAX_CRO_SUPPLY = 30_000_000_000  # max CRO supply: 30 billion


class CROCoin:
    def __init__(
        self,
        amount: "Union[int, float, str, decimal.Decimal]",
        unit: str,
        network_config: "NetworkConfig",
    ) -> None:
        """
        Parameters
        ----------
            amount : int, float, str, decimal.Decimal
                The amount of coin

                To avoid precision issues in Python,
                "str" and "decimal.Decimal" types are highly recommended
            unit : str
                One of coin_denom and coin_base_denom from network_config
            network_config : NetworkConfig
                Network configuration to interact with the chain
        """
        assert unit in [network_config.coin_denom, network_config.coin_base_denom], (
            f"unit should be {network_config.coin_denom} or "
            f"{network_config.coin_base_denom}, got {unit}"
        )

        self._denom = network_config.coin_denom
        self._base_denom = network_config.coin_base_denom
        self._exponent = network_config.exponent
        self._unit = unit
        self._network_config = network_config
        self.amount_base = amount  # type:ignore
        # pending https://github.com/python/mypy/issues/3004 to remove above type:ignore

    @property
    def amount_base(self) -> str:
        """Returns Coin amount only, in base denom unit.

        ("1cro" is returned as "100000000")
        """
        return self._amount_base

    @amount_base.setter
    def amount_base(self, amount: Union[int, float, str, "decimal.Decimal"]) -> None:
        temp_base_amount = self._to_number_in_base(amount, self._unit)

        if "." in temp_base_amount:
            raise ValueError(f"Amount is less than 1{self._base_denom}")
        if int(temp_base_amount) > MAX_CRO_SUPPLY * 10**self._exponent:
            raise ValueError(
                "Input is more than maximum cro supply"
                f" {MAX_CRO_SUPPLY * 10 ** self._exponent}{self._base_denom}"
                f" got {temp_base_amount}{self._base_denom}"
            )
        if int(temp_base_amount) < 0:
            raise ValueError("Amount cannot be negative")

        self._amount_base = temp_base_amount

    @property
    def amount(self) -> str:
        """Returns Coin amount only, in denom unit.

        ("1cro" is returned as "1")
        """
        return self._from_number_in_base(self.amount_base, self._denom)

    @property
    def amount_with_unit(self) -> str:
        """Returns converted Coin amount with denom unit.

        (e.g. "10cro").
        """
        return f"{self.amount}{self._denom}"

    @property
    def amount_base_with_unit(self) -> str:
        """Returns converted Coin amount with base denom unit.

        (e.g. "100000basecro").
        """
        return f"{self.amount_base}{self._base_denom}"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, CROCoin):
            return NotImplemented
        return self.amount_base == __o.amount_base

    def _cast_to_str(self, number: Union[int, float, decimal.Decimal]) -> str:
        """Cast number to string format.

        Remove trailing "0" and "." if necessary
        """
        s_number = "{:f}".format(number)

        if "." in s_number:
            s_number = s_number.rstrip("0").rstrip(".")
        return s_number

    def _cast_to_Decimal_obj(
        self, number: Union[int, float, str, "decimal.Decimal"]
    ) -> "decimal.Decimal":
        if is_integer(number) or isinstance(number, str):
            d_number = decimal.Decimal(value=number)
        elif isinstance(number, float):
            d_number = decimal.Decimal(value=str(number))
        elif isinstance(number, decimal.Decimal):
            d_number = number
        else:
            raise TypeError("Unsupported type.  Must be one of integer, float, or string")

        return d_number

    def _get_conversion_rate_to_base_unit(self, unit: str) -> decimal.Decimal:
        """Takes a unit and gets its conversion rate to the base unit."""
        if unit == self._denom:
            return decimal.Decimal(value=10**self._exponent)
        elif unit == self._base_denom:
            return decimal.Decimal(1)
        else:
            raise ValueError(
                f"Expect denom to be {self._denom} or {self._base_denom}, got ${unit}"
            )

    def _from_number_in_base(self, number: str, unit: str) -> str:
        """Takes an amount of base denom and converts it to an amount of other
        denom unit."""
        if number == "0":
            return "0"

        unit_conversion = self._get_conversion_rate_to_base_unit(unit)

        with decimal.localcontext() as ctx:
            ctx.prec = 999
            d_number = decimal.Decimal(value=number, context=ctx)
            result_value = d_number / unit_conversion

        return self._cast_to_str(result_value)

    def _to_number_in_base(
        self, number: Union[int, float, str, "decimal.Decimal"], unit: str
    ) -> str:
        """Takes a number of a unit and converts it to a number of the base
        denom."""
        d_number = self._cast_to_Decimal_obj(number)

        s_number = str(number)
        unit_conversion = self._get_conversion_rate_to_base_unit(unit)

        if d_number == decimal.Decimal(0):
            return "0"

        if d_number < 1 and "." in s_number:
            with decimal.localcontext() as ctx:
                multiplier = len(s_number) - s_number.index(".") - 1
                ctx.prec = multiplier
                d_number = decimal.Decimal(value=number, context=ctx) * 10**multiplier
            unit_conversion /= 10**multiplier

        with decimal.localcontext() as ctx:
            ctx.prec = 999
            result_value = decimal.Decimal(value=d_number, context=ctx) * unit_conversion

        return self._cast_to_str(result_value)

    @property
    def single_coin(self) -> "SingleCoin":
        """Returns DeFi Wallet Core representation."""
        return SingleCoin.OTHER(self.amount_base, self._base_denom)

    @property
    def amino_coin_message(self) -> Dict[str, str]:
        """Returns json amino compatiable Coin message."""
        return {"amount": self.amount_base, "denom": self._base_denom}

    def __add__(self, __o: object) -> "CROCoin":
        if not isinstance(__o, CROCoin):
            return NotImplemented

        with decimal.localcontext() as ctx:
            ctx.prec = 999
            result_value = decimal.Decimal(self.amount_base) + decimal.Decimal(__o.amount_base)

        return type(self)(result_value, self._base_denom, self._network_config)

    def __sub__(self, __o: object) -> "CROCoin":
        if not isinstance(__o, CROCoin):
            return NotImplemented

        with decimal.localcontext() as ctx:
            ctx.prec = 999
            result_value = decimal.Decimal(self.amount_base) - decimal.Decimal(__o.amount_base)

        return type(self)(result_value, self._base_denom, self._network_config)
