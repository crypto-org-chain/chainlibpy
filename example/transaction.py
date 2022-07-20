#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from chainlibpy import CROCoin, GrpcClient, Transaction, Wallet
from chainlibpy.generated.common import CosmosSdkMsg
from chainlibpy.grpc_client import NetworkConfig

# Recommend to use [pystarport](https://pypi.org/project/pystarport/) to setup a testnet locally
# To use testnet configs in local_testnet_configs with pystarport:
# 1. Download corresponding chain-maind binary from https://github.com/crypto-org-chain/chain-main/releases # noqa: 501
# 2. Copy chain-maind binary to `./example` directory
# 3. Enter `poetry shell`
# 4. Go to `./example` directory
# 5. Run Command `pystarport serve --data=./data --config=./local_testnet_configs/default.yaml --cmd=./chain-maind` # noqa: 501
# 6. Obtain `MNEMONIC_PHRASE` and `TO_ADDRESS` accordingly
# 7. Open another terminal window and run examples in this file

# Obtained from {directory_started_pystarport}/data/chainmaind/accounts.json
# To recover one of the genesis account
MNEMONIC_PHRASE = "first ... last"
# Obtained from {directory_started_pystarport}/data/chainmaind/accounts.json
TO_ADDRESS = "cro...add"

LOCAL_NETWORK = NetworkConfig(
    # grpc_endpoint from {directory_started_pystarport}/data/chaintest/nodex/config/app.toml
    # Look for "gRPC Configuration" section
    grpc_endpoint="http://127.0.0.1:26653",
    tendermint_rpc="http://127.0.0.1:26657",
    rest_api="http://127.0.0.1:26658",
    # chain_id from from {directory_started_pystarport}/data/
    # the directory name under data is the chain_id
    chain_id="chaintest",
    address_prefix="cro",
    coin_denom="cro",
    coin_base_denom="basecro",
    exponent=8,
    derivation_path="m/44'/394'/0'/0/0",
)


def simple_transaction():
    client = GrpcClient(LOCAL_NETWORK)

    sending_wallet = Wallet(
        MNEMONIC_PHRASE, LOCAL_NETWORK.derivation_path, LOCAL_NETWORK.address_prefix
    )
    sending_account = client.query_account(sending_wallet.address)
    sending_account_init_bal = client.query_account_balance(sending_wallet.address)
    receiving_account_init_bal = client.query_account_balance(TO_ADDRESS)

    print(
        f"sending account initial balance: {sending_account_init_bal.amount}"
        f"{sending_account_init_bal.denom}"
    )
    print(
        f"receiving account initial balance: {receiving_account_init_bal.amount}"
        f"{receiving_account_init_bal.denom}"
    )

    ten_cro = CROCoin("10", "cro", LOCAL_NETWORK)
    one_cro_fee = CROCoin("1", "cro", LOCAL_NETWORK)

    msg_send = CosmosSdkMsg.BANK_SEND(
        TO_ADDRESS,
        ten_cro.single_coin,
    )
    tx = Transaction(
        chain_id=LOCAL_NETWORK.chain_id,
        from_wallet=sending_wallet,
        msgs=[msg_send],
        account_number=sending_account.account_number,
        fee=one_cro_fee.single_coin,
        client=client,
    )

    signed_tx = tx.signed_tx

    client.broadcast_transaction(signed_tx)

    sending_account_aft_bal = client.query_account_balance(sending_wallet.address)
    receiving_account_aft_bal = client.query_account_balance(TO_ADDRESS)

    print("After transaction of sending 10cro with a 1cro fee:")
    print(
        f"sending account after balance: {sending_account_aft_bal.amount}"
        f"{sending_account_aft_bal.denom}"
    )
    print(
        f"receiving account after balance: {receiving_account_aft_bal.amount}"
        f"{receiving_account_aft_bal.denom}"
    )


def transaction_with_two_messages():
    client = GrpcClient(LOCAL_NETWORK)

    sending_wallet = Wallet(
        MNEMONIC_PHRASE, LOCAL_NETWORK.derivation_path, LOCAL_NETWORK.address_prefix
    )
    sending_account = client.query_account(sending_wallet.address)
    sending_account_init_bal = client.query_account_balance(sending_wallet.address)
    receiving_account_init_bal = client.query_account_balance(TO_ADDRESS)

    print(
        f"sending account initial balance  : {sending_account_init_bal.amount}"
        f"{sending_account_init_bal.denom}"
    )
    print(
        f"receiving account initial balance: {receiving_account_init_bal.amount}"
        f"{receiving_account_init_bal.denom}"
    )

    one_hundred_cro = CROCoin("100", "cro", LOCAL_NETWORK)
    two_hundred_cro = CROCoin("200", "cro", LOCAL_NETWORK)
    one_cro_fee = CROCoin("1", "cro", LOCAL_NETWORK)

    msg_send_100_cro = CosmosSdkMsg.BANK_SEND(
        TO_ADDRESS,
        one_hundred_cro.single_coin,
    )
    msg_send_200_cro = CosmosSdkMsg.BANK_SEND(
        TO_ADDRESS,
        two_hundred_cro.single_coin,
    )
    tx = Transaction(
        chain_id=LOCAL_NETWORK.chain_id,
        from_wallet=sending_wallet,
        msgs=[msg_send_100_cro],
        account_number=sending_account.account_number,
        fee=one_cro_fee.single_coin,
        client=client,
    )
    tx.append_message(msg_send_200_cro)

    signed_tx = tx.signed_tx

    client.broadcast_transaction(signed_tx)

    sending_account_aft_bal = client.query_account_balance(sending_wallet.address)
    receiving_account_aft_bal = client.query_account_balance(TO_ADDRESS)
    sending_account_cro = CROCoin(
        sending_account_aft_bal.amount,
        sending_account_aft_bal.denom,
        LOCAL_NETWORK,
    )
    receiving_account_cro = CROCoin(
        receiving_account_aft_bal.amount,
        receiving_account_aft_bal.denom,
        LOCAL_NETWORK,
    )

    print("After transaction of sending 300cro in total with a 1cro fee:")
    print(f"sending account after balance  : {sending_account_cro.amount_with_unit}")
    print(f"receiving account after balance: {receiving_account_cro.amount_with_unit}")


if __name__ == "__main__":
    simple_transaction()
    transaction_with_two_messages()
