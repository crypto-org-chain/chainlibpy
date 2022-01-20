#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from chainlibpy.generated.cosmos.base.v1beta1.coin_pb2 import Coin
from chainlibpy.grpc_client import GrpcClient
from chainlibpy.wallet import Wallet

# NOTE:
# Recommend to use pystarport(https://pypi.org/project/pystarport/) to setup a testnet locally

DENOM = "basecro"
# Obtained from {directory_started_pystarport}/data/chainmaind/accounts.json
# To recover one of the genesis account
# MNEMONIC_PHRASE = "first ... last"
MNEMONIC_PHRASE = "hurry exist clerk safe aware anchor brush run dentist come surge frame tired economy school grief volcano enforce word alpha liar clever sure taxi"
# Obtained from {directory_started_pystarport}/data/chainmaind/accounts.json
# Another address to receive coins sent
TO_ADDRESS = "cro1hk220qwxp0c8m3pzazardmmfv8y0mg7ukdnn37"
AMOUNT = [Coin(amount="10000", denom=DENOM)]
# Obtained from {directory_started_pystarport}/data/chainmaind/genesis.json
CHAIN_ID = "chain_id_test"
# Obtained from {directory_started_pystarport}/data/chainmaind/nodex/config/app.toml
# Look for "gRPC Configuration" section
GRPC_ENDPOINT = "0.0.0.0:26653"


def main():
    wallet = Wallet(MNEMONIC_PHRASE)
    client = GrpcClient(CHAIN_ID, DENOM, GRPC_ENDPOINT)

    from_address = wallet.address
    res = client.get_balance(from_address)
    print(f"from_address initial balance: {res.balance.amount}")
    # res = client.get_balance(TO_ADDRESS, DENOM)
    # print(f"to_address initial balance: {res.balance.amount}")
    client.bank_send(wallet.address, wallet.private_key, wallet.public_key, TO_ADDRESS, AMOUNT)

    print("after successful transaction")
    res = client.get_balance(from_address)
    print(f"from_address updated balance: {res.balance.amount}")
    res = client.get_balance(TO_ADDRESS)
    print(f"to_address updated balance: {res.balance.amount}")


if __name__ == "__main__":
    main()
