import pytest

from chainlibpy import (
    CRO_NETWORK,
    CROCoin,
    GrpcClient,
    NetworkConfig,
    Transaction,
    Wallet,
)
from chainlibpy.generated.common import CosmosSdkMsg

from .utils import ALICE, BOB, CRO_DENOM, get_blockchain_account_info


@pytest.mark.parametrize("network_config", CRO_NETWORK.values())
def test_network_config(network_config: "NetworkConfig"):

    client = GrpcClient(network_config)

    assert (
        client.query_bank_denom_metadata(network_config.coin_base_denom).base
        == network_config.coin_base_denom
    )


def test_send_cro(blockchain_accounts, local_test_network_config: "NetworkConfig"):
    client = GrpcClient(local_test_network_config)
    alice_info = get_blockchain_account_info(blockchain_accounts, ALICE)
    alice_wallet = Wallet(alice_info["mnemonic"])
    alice_account = client.query_account(alice_info["address"])
    bob_info = get_blockchain_account_info(blockchain_accounts, BOB)
    bob_wallet = Wallet(bob_info["mnemonic"])
    alice_bal_init = client.query_account_balance(alice_wallet.address)
    bob_bal_init = client.query_account_balance(bob_wallet.address)
    alice_coin_init = CROCoin(
        alice_bal_init.amount, alice_bal_init.denom, local_test_network_config
    )
    bob_coin_init = CROCoin(bob_bal_init.amount, bob_bal_init.denom, local_test_network_config)

    ten_cro = CROCoin("10", CRO_DENOM, local_test_network_config)
    one_cro_fee = CROCoin("1", CRO_DENOM, local_test_network_config)
    msg_send = CosmosSdkMsg.BANK_SEND(
        bob_info["address"],
        ten_cro.single_coin,
    )

    tx = Transaction(
        chain_id=local_test_network_config.chain_id,
        from_wallet=alice_wallet,
        msgs=[msg_send],
        account_number=alice_account.account_number,
        fee=one_cro_fee.single_coin,
        client=client,
    )

    signed_tx = tx.signed_tx

    client.broadcast_transaction(signed_tx)
    alice_bal_aft = client.query_account_balance(alice_wallet.address)
    bob_bal_aft = client.query_account_balance(bob_wallet.address)
    alice_coin_aft = CROCoin(alice_bal_aft.amount, alice_bal_aft.denom, local_test_network_config)
    bob_coin_aft = CROCoin(bob_bal_aft.amount, bob_bal_aft.denom, local_test_network_config)

    assert alice_coin_aft == alice_coin_init - ten_cro - one_cro_fee
    assert bob_coin_aft == bob_coin_init + ten_cro


def test_2_msgs_in_1_tx(blockchain_accounts, local_test_network_config: "NetworkConfig"):
    client = GrpcClient(local_test_network_config)
    alice_info = get_blockchain_account_info(blockchain_accounts, ALICE)
    alice_wallet = Wallet(alice_info["mnemonic"])
    alice_account = client.query_account(alice_info["address"])
    bob_info = get_blockchain_account_info(blockchain_accounts, BOB)
    bob_wallet = Wallet(bob_info["mnemonic"])
    alice_bal_init = client.query_account_balance(alice_wallet.address)
    bob_bal_init = client.query_account_balance(bob_wallet.address)
    alice_coin_init = CROCoin(
        alice_bal_init.amount, alice_bal_init.denom, local_test_network_config
    )
    bob_coin_init = CROCoin(bob_bal_init.amount, bob_bal_init.denom, local_test_network_config)

    ten_cro = CROCoin("10", CRO_DENOM, local_test_network_config)
    twnenty_cro = CROCoin("20", CRO_DENOM, local_test_network_config)
    one_cro_fee = CROCoin("1", CRO_DENOM, local_test_network_config)
    msg_send_10_cro = CosmosSdkMsg.BANK_SEND(
        bob_info["address"],
        ten_cro.single_coin,
    )
    msg_send_20_cro = CosmosSdkMsg.BANK_SEND(
        bob_info["address"],
        twnenty_cro.single_coin,
    )

    tx = Transaction(
        chain_id=local_test_network_config.chain_id,
        from_wallet=alice_wallet,
        msgs=[msg_send_10_cro],
        account_number=alice_account.account_number,
        fee=one_cro_fee.single_coin,
        client=client,
    ).append_message(msg_send_20_cro)

    signed_tx = tx.signed_tx

    client.broadcast_transaction(signed_tx)
    alice_bal_aft = client.query_account_balance(alice_wallet.address)
    bob_bal_aft = client.query_account_balance(bob_wallet.address)
    alice_coin_aft = CROCoin(alice_bal_aft.amount, alice_bal_aft.denom, local_test_network_config)
    bob_coin_aft = CROCoin(bob_bal_aft.amount, bob_bal_aft.denom, local_test_network_config)

    assert alice_coin_aft == alice_coin_init - ten_cro - twnenty_cro - one_cro_fee
    assert bob_coin_aft == bob_coin_init + ten_cro + twnenty_cro
