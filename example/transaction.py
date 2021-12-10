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
MNEMONIC_PHRASE = "first ... last"
# Obtained from {directory_started_pystarport}/data/chainmaind/accounts.json
# Another address to receive coins sent
TO_ADDRESS = "cro...add"
AMOUNT = [Coin(amount="10000", denom=DENOM)]
# Obtained from {directory_started_pystarport}/data/chainmaind/genesis.json
CHAIN_ID = "chainmaind"
# Obtained from {directory_started_pystarport}/data/chainmaind/nodex/config/app.toml
# Look for "gRPC Configuration" section
GRPC_ENDPOINT = "0.0.0.0:26653"


def main():
    wallet = Wallet(MNEMONIC_PHRASE)
    client = GrpcClient(wallet, CHAIN_ID, GRPC_ENDPOINT)

    from_address = wallet.address
    res = client.get_balance(from_address, DENOM)
    print(f"from_address initial balance: {res.balance.amount}")
    res = client.get_balance(TO_ADDRESS, DENOM)
    print(f"to_address initial balance: {res.balance.amount}")

    client.bank_send(TO_ADDRESS, AMOUNT)

    print("after successful transaction")
    res = client.get_balance(from_address, DENOM)
    print(f"from_address updated balance: {res.balance.amount}")
    res = client.get_balance(TO_ADDRESS, DENOM)
    print(f"to_address updated balance: {res.balance.amount}")


if __name__ == "__main__":
    main()
