# Copyright (c) 2020, hukkinj1 (licensed under the MIT License)
# Modifications Copyright (c) 2020, Foris Limited (licensed under the Apache License, Version 2.0)

from chainlibpy import Transaction, Wallet
from chainlibpy.amino import Coin, StdFee
from chainlibpy.amino.message import MsgSend


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
            "timeout_height": "0",
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

    std_fee = StdFee("30000", [Coin(str(fee))])
    tx = Transaction(
        wallet=wallet,
        account_num=11335,
        sequence=0,
        fee=std_fee,
        chain_id="test",
    )
    msg = MsgSend(
        wallet.address,
        "cro103l758ps7403sd9c0y8j6hrfw4xyl70j4mmwkf",
        [Coin(str(amount))],
    )
    tx.add_msg(msg)
    pushable_tx = tx.get_pushable()
    assert pushable_tx == expected_pushable_tx
