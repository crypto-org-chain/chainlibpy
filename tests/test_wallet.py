# Copyright (c) 2020, hukkinj1 (licensed under the MIT License)
# Modifications Copyright (c) 2020, Foris Limited (licensed under the Apache License, Version 2.0)

from chainlibpy import Wallet


def test_generate_wallet():
    seed = "burst negative solar evoke traffic yard lizard next series foster seminar enter wrist captain bulb trap giggle country sword season shoot boy bargain deal"
    wallet = Wallet(seed)
    assert wallet.private_key == bytes.fromhex(
        "dc81c553efffdce74035a194ea7a58f1d67bdfd1329e33f684460d9ed6223faf"
    )
    assert wallet.public_key == bytes.fromhex(
        "02089cf50d9fc7d98e650dadd5569671ccc6389d845b00dfbcfc01bd5b58969a0c"
    )
    assert wallet.address == "cro1yj3fd8gxrqd2662p8ywp26t4hfws9p5n75xjum"


def test_new_wallet():
    wallet = Wallet.new()
    assert len(str(wallet.private_key)) > 0
