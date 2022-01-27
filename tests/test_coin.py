import decimal

import hypothesis.strategies as st
import pytest
from hypothesis import example, given

from chainlibpy import MAX_CRO_SUPPLY, CROCoin, NetworkConfig

from .utils import BASECRO_DENOM, CRO_DENOM

################################
# Important:
# test cases are designed based on the assumption:
# 1cro is equal to 10**8basecro
################################


@given(amount=st.integers(min_value=0, max_value=MAX_CRO_SUPPLY))
@example(amount=0)
@example(amount=MAX_CRO_SUPPLY)
def test_crocoin_with_integer_amount(local_test_network_config: "NetworkConfig", amount):
    coin_with_denom = CROCoin(
        amount, local_test_network_config.coin_denom, local_test_network_config
    )
    coin_with_base_denom = CROCoin(
        coin_with_denom.amount_base,
        local_test_network_config.coin_base_denom,
        local_test_network_config,
    )

    assert coin_with_denom == coin_with_base_denom


@pytest.mark.parametrize(
    "amount, expected_amount, expected_base_amount",
    [
        (0, "0", "0"),
        ("0", "0", "0"),
        (decimal.Decimal(value="0"), "0", "0"),
        (1, "1", "100000000"),
        ("1", "1", "100000000"),
        (decimal.Decimal(value="1"), "1", "100000000"),
        (1.0, "1", "100000000"),
        ("1.0", "1", "100000000"),
        (decimal.Decimal(value="1.0"), "1", "100000000"),
        (34.5, "34.5", "3450000000"),
        ("34.5", "34.5", "3450000000"),
        (decimal.Decimal(value="34.5"), "34.5", "3450000000"),
        (0.8, "0.8", "80000000"),
        ("0.8", "0.8", "80000000"),
        (decimal.Decimal(value="0.8"), "0.8", "80000000"),
        (1000001, "1000001", "100000100000000"),
        ("1000001", "1000001", "100000100000000"),
        (decimal.Decimal(value="1000001"), "1000001", "100000100000000"),
        (MAX_CRO_SUPPLY, str(MAX_CRO_SUPPLY), "3000000000000000000"),
        (str(MAX_CRO_SUPPLY), str(MAX_CRO_SUPPLY), "3000000000000000000"),
        (decimal.Decimal(value=MAX_CRO_SUPPLY), str(MAX_CRO_SUPPLY), "3000000000000000000"),
        (29999999999, "29999999999", "2999999999900000000"),
        ("29999999999", "29999999999", "2999999999900000000"),
        (decimal.Decimal(value="29999999999"), "29999999999", "2999999999900000000"),
        ("29999999999.99999999", "29999999999.99999999", "2999999999999999999"),
        (
            decimal.Decimal(value="29999999999.99999999"),
            "29999999999.99999999",
            "2999999999999999999",
        ),
        (12170000, "12170000", "1217000000000000"),
        ("12170000", "12170000", "1217000000000000"),
        (decimal.Decimal(value="12170000"), "12170000", "1217000000000000"),
        (0.8000, "0.8", "80000000"),
        ("0.8000", "0.8", "80000000"),
        (decimal.Decimal(value="0.8000"), "0.8", "80000000"),
        (0.63000001, "0.63000001", "63000001"),
        ("0.63000001", "0.63000001", "63000001"),
        (decimal.Decimal(value="0.63000001"), "0.63000001", "63000001"),
        (0.00000001, "0.00000001", "1"),
        ("0.00000001", "0.00000001", "1"),
        (decimal.Decimal(value="0.00000001"), "0.00000001", "1"),
        (50000000.00000001, "50000000.00000001", "5000000000000001"),
        ("50000000.00000001", "50000000.00000001", "5000000000000001"),
        (decimal.Decimal(value="50000000.00000001"), "50000000.00000001", "5000000000000001"),
        (0.99999999, "0.99999999", "99999999"),
        ("0.99999999", "0.99999999", "99999999"),
        (decimal.Decimal(value="0.99999999"), "0.99999999", "99999999"),
    ],
)
def test_crocoin_with_denom_input(
    local_test_network_config: "NetworkConfig", amount, expected_amount, expected_base_amount
):
    cro_coin = CROCoin(amount, local_test_network_config.coin_denom, local_test_network_config)

    assert cro_coin.amount == expected_amount
    assert cro_coin.amount_with_unit == f"{expected_amount}{local_test_network_config.coin_denom}"
    assert cro_coin.amount_base == expected_base_amount
    assert (
        cro_coin.amount_base_with_unit
        == f"{expected_base_amount}{local_test_network_config.coin_base_denom}"
    )


@pytest.mark.parametrize(
    "base_amount, expected_base_amount, expected_amount",
    [
        (0, "0", "0"),
        ("0", "0", "0"),
        (decimal.Decimal(value="0"), "0", "0"),
        (1, "1", "0.00000001"),
        ("1", "1", "0.00000001"),
        (decimal.Decimal(value="1"), "1", "0.00000001"),
        (800, "800", "0.000008"),
        ("800", "800", "0.000008"),
        (decimal.Decimal(value="800"), "800", "0.000008"),
        (3000000000000000000, "3000000000000000000", str(MAX_CRO_SUPPLY)),
        ("3000000000000000000", "3000000000000000000", str(MAX_CRO_SUPPLY)),
        (decimal.Decimal(value="3000000000000000000"), "3000000000000000000", str(MAX_CRO_SUPPLY)),
        (2999999999999999999, "2999999999999999999", "29999999999.99999999"),
        ("2999999999999999999", "2999999999999999999", "29999999999.99999999"),
        (
            decimal.Decimal(value="2999999999999999999"),
            "2999999999999999999",
            "29999999999.99999999",
        ),
        (5000000000000001, "5000000000000001", "50000000.00000001"),
        ("5000000000000001", "5000000000000001", "50000000.00000001"),
        (decimal.Decimal(value="5000000000000001"), "5000000000000001", "50000000.00000001"),
        (1300001400000, "1300001400000", "13000.014"),
        ("1300001400000", "1300001400000", "13000.014"),
        (decimal.Decimal(value="1300001400000"), "1300001400000", "13000.014"),
        (99999999, "99999999", "0.99999999"),
        ("99999999", "99999999", "0.99999999"),
        (decimal.Decimal(value="99999999"), "99999999", "0.99999999"),
    ],
)
def test_crocoin_with_base_denom_input(
    local_test_network_config: "NetworkConfig", base_amount, expected_base_amount, expected_amount
):
    cro_coin = CROCoin(
        base_amount, local_test_network_config.coin_base_denom, local_test_network_config
    )

    assert cro_coin.amount == expected_amount
    assert cro_coin.amount_with_unit == f"{expected_amount}{local_test_network_config.coin_denom}"
    assert cro_coin.amount_base == expected_base_amount
    assert (
        cro_coin.amount_base_with_unit
        == f"{expected_base_amount}{local_test_network_config.coin_base_denom}"
    )


@pytest.mark.parametrize(
    "amount, wrong_unit",
    [
        ("1", "not-a-unit"),
        (str(MAX_CRO_SUPPLY + 1), "not-a-unit"),
        (-1, "not-a-unit"),
    ],
)
def test_crocoin_with_wrong_unit_should_raise_exception(
    amount, wrong_unit, local_test_network_config: "NetworkConfig"
):
    with pytest.raises(
        AssertionError,
        match=f"unit should be {local_test_network_config.coin_denom} or {local_test_network_config.coin_base_denom}, got {wrong_unit}",  # noqa 501
    ):
        CROCoin(amount, wrong_unit, local_test_network_config)


@pytest.mark.parametrize(
    "invalid_amount, unit, invalid_amount_base",
    [
        (MAX_CRO_SUPPLY + 1, CRO_DENOM, "3000000000100000000"),
        (str(MAX_CRO_SUPPLY + 1), CRO_DENOM, "3000000000100000000"),
        (decimal.Decimal(value=str(MAX_CRO_SUPPLY + 1)), CRO_DENOM, "3000000000100000000"),
        ("30000000000.00000001", CRO_DENOM, "3000000000000000001"),
        (decimal.Decimal(value="30000000000.00000001"), CRO_DENOM, "3000000000000000001"),
        (MAX_CRO_SUPPLY * 10 ** 8 + 1, BASECRO_DENOM, "3000000000000000001"),
        (str(MAX_CRO_SUPPLY * 10 ** 8 + 1), BASECRO_DENOM, "3000000000000000001"),
        (
            decimal.Decimal(value=str(MAX_CRO_SUPPLY * 10 ** 8 + 1)),
            BASECRO_DENOM,
            "3000000000000000001",
        ),
    ],
)
def test_crocoin_beyond_max_supply_should_raise_exception(
    invalid_amount, unit, invalid_amount_base, local_test_network_config: "NetworkConfig"
):

    with pytest.raises(
        ValueError,
        match=rf"^Input is more than maximum cro supply .* got {invalid_amount_base}basecro$",  # noqa 501
    ):
        CROCoin(invalid_amount, unit, local_test_network_config)


@pytest.mark.parametrize(
    "below_zero_amount, unit",
    [
        (-1, CRO_DENOM),
        ("-1", CRO_DENOM),
        (decimal.Decimal(value="-1"), CRO_DENOM),
        ("-0.00000001", CRO_DENOM),
        (decimal.Decimal(value="-0.00000001"), CRO_DENOM),
        (-1, BASECRO_DENOM),
        ("-1", BASECRO_DENOM),
        (decimal.Decimal(value="-1"), BASECRO_DENOM),
    ],
)
def test_crocoin_below_zero_should_raise_exception(
    below_zero_amount, unit, local_test_network_config: "NetworkConfig"
):
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        CROCoin(below_zero_amount, unit, local_test_network_config)


@pytest.mark.parametrize(
    "invalid_amount, unit",
    [
        (0.1, BASECRO_DENOM),
        ("0.000000000000000000000000000000000000000000000000001", BASECRO_DENOM),
        (
            decimal.Decimal(value="0.000000000000000000000000000000000000000000000000001"),
            BASECRO_DENOM,
        ),
        ("0.00000000000001", CRO_DENOM),
        ("50000000.00000000000001", CRO_DENOM),
    ],
)
def test_crocoin_temp(invalid_amount, unit, local_test_network_config: "NetworkConfig"):
    with pytest.raises(ValueError, match="Amount is less than 1basecro"):
        CROCoin(invalid_amount, unit, local_test_network_config)
