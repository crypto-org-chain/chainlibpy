# Copyright (c) 2020, hukkinj1 (licensed under the MIT License)
# Modifications Copyright (c) 2020, Foris Limited (licensed under the Apache License, Version 2.0)

from unittest.mock import Mock

from chainlibpy import Transaction, Wallet


def test_sign():
    unordered_sign_message = {
        "chain_id": "tendermint_test",
        "account_number": "1",
        "fee": {"gas": "21906", "amount": [{"amount": "0", "denom": ""}]},
        "memo": "",
        "sequence": "0",
        "msgs": [
            {
                "type": "cosmos-sdk/Send",
                "value": {
                    "inputs": [
                        {
                            "address": "tcro1qperwt9wrnkg5k9e5gzfgjppzpqhyav5j24d66",
                            "coins": [{"amount": "1", "denom": "STAKE"}],
                        }
                    ],
                    "outputs": [
                        {
                            "address": "tcro1yeckxz7tapz34kjwnjxvmxzurerquhtrmxmuxt",
                            "coins": [{"amount": "1", "denom": "STAKE"}],
                        }
                    ],
                },
            }
        ],
    }
    seed = "dune car envelope chuckle elbow slight proud fury remove candy uphold puzzle call select sibling sport gadget please want vault glance verb damage gown"
    wallet = Wallet(seed)
    dummy_num = 1337
    tx = Transaction(
        wallet=wallet,
        account_num=dummy_num,
        sequence=dummy_num,
        fee=dummy_num,
        gas=dummy_num,
    )
    tx._get_sign_message = Mock(return_value=unordered_sign_message)  # type: ignore

    expected_signature = "s2Yz6UjEpLJuNcyWn5E2adUu5Vn7gbKwrtyoBrQWEhUTomnxlASRnP/1GD/j1MD4PeJsNtE0MOjwOyFt8dU2cw=="

    actual_signature = tx._sign()
    assert actual_signature == expected_signature


def test_get_pushable_tx():
    expected_pushable_tx = {
        "tx": {
            "msg": [
                {
                    "type": "cosmos-sdk/MsgSend",
                    "value": {
                        "from_address": "cro1u9q8mfpzhyv2s43js7l5qseapx5kt3g2rf7ppf",
                        "to_address": "cro103l758ps7403sd9c0y8j6hrfw4xyl70j4mmwkf",
                        "amount": [{"denom": "basecro", "amount": "288000"}],
                    },
                }
            ],
            "fee": {
                "gas": "30000",
                "amount": [{"amount": "100000", "denom": "basecro"}],
            },
            "memo": "",
            "signatures": [
                {
                    "signature": "WjB3aB3k/nUK33iyGvbMPu55iiyCJBr7ooKQXwxE1BFAdBjJXIblp1aVPUjlr/blFAlHW7fLJct9zc/7ty8ZQA==",
                    "pub_key": {
                        "type": "tendermint/PubKeySecp256k1",
                        "value": "AntL+UxMyJ9NZ9DGLp2v7a3dlSxiNXMaItyOXSRw8iYi",
                    },
                    "account_number": "11335",
                    "sequence": "0",
                }
            ],
        },
        "mode": "sync",
    }
    seed = "dune car envelope chuckle elbow slight proud fury remove candy uphold puzzle call select sibling sport gadget please want vault glance verb damage gown"
    wallet = Wallet(seed)
    fee = 100000
    _tx_total_cost = 388000
    amount = _tx_total_cost - fee

    tx = Transaction(
        wallet=wallet,
        account_num=11335,
        sequence=0,
        fee=fee,
        gas=30000,
        chain_id="test",
    )
    tx.add_transfer(
        to_address="cro103l758ps7403sd9c0y8j6hrfw4xyl70j4mmwkf", amount=amount
    )
    pushable_tx = tx.get_pushable()
    assert pushable_tx == expected_pushable_tx
