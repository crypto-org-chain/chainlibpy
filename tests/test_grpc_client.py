import socket
import ssl

import grpc
import pytest

from chainlibpy import (
    CRO_NETWORK,
    CROCoin,
    GrpcClient,
    NetworkConfig,
    Transaction,
    Wallet,
)
from chainlibpy.generated.cosmos.bank.v1beta1.tx_pb2 import MsgSend

from .utils import ALICE, BOB, CRO_DENOM, get_blockchain_account_info


@pytest.mark.parametrize("network_config", CRO_NETWORK.values())
def test_network_config(network_config: "NetworkConfig"):
    (server_host, server_port) = network_config.grpc_endpoint.split(":")

    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    with socket.create_connection((server_host, int(server_port))) as sock:
        with context.wrap_socket(sock, server_hostname=server_host) as ssock:
            certificate_DER = ssock.getpeercert(True)

    if certificate_DER is None:
        pytest.fail("no certificate returned from server")

    certificate_PEM = ssl.DER_cert_to_PEM_cert(certificate_DER)
    creds = grpc.ssl_channel_credentials(str.encode(certificate_PEM))
    client = GrpcClient(network_config, creds)

    assert (
        client.query_bank_denom_metadata(network_config.coin_base_denom).metadata.base
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
        alice_bal_init.balance.amount, alice_bal_init.balance.denom, local_test_network_config
    )
    bob_coin_init = CROCoin(
        bob_bal_init.balance.amount, bob_bal_init.balance.denom, local_test_network_config
    )

    ten_cro = CROCoin("10", CRO_DENOM, local_test_network_config)
    one_cro_fee = CROCoin("1", CRO_DENOM, local_test_network_config)
    msg_send = MsgSend(
        from_address=alice_info["address"],
        to_address=bob_info["address"],
        amount=[ten_cro.protobuf_coin_message],
    )

    tx = Transaction(
        chain_id=local_test_network_config.chain_id,
        from_wallets=[alice_wallet],
        msgs=[msg_send],
        account_number=alice_account.account_number,
        fee=[one_cro_fee.protobuf_coin_message],
        client=client,
    )

    sign_doc = tx.get_sign_doc()
    signature_alice = alice_wallet.sign(sign_doc.SerializeToString())
    signed_tx = tx.get_signed_tx([signature_alice])

    client.broadcast_transaction_block_mode(signed_tx.SerializeToString())

    alice_bal_aft = client.query_account_balance(alice_wallet.address)
    bob_bal_aft = client.query_account_balance(bob_wallet.address)
    alice_coin_aft = CROCoin(
        alice_bal_aft.balance.amount, alice_bal_aft.balance.denom, local_test_network_config
    )
    bob_coin_aft = CROCoin(
        bob_bal_aft.balance.amount, bob_bal_aft.balance.denom, local_test_network_config
    )

    assert alice_coin_aft == alice_coin_init.minus(ten_cro).minus(one_cro_fee)
    assert bob_coin_aft == bob_coin_init.plus(ten_cro)


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
        alice_bal_init.balance.amount, alice_bal_init.balance.denom, local_test_network_config
    )
    bob_coin_init = CROCoin(
        bob_bal_init.balance.amount, bob_bal_init.balance.denom, local_test_network_config
    )

    ten_cro = CROCoin("10", CRO_DENOM, local_test_network_config)
    twnenty_cro = CROCoin("20", CRO_DENOM, local_test_network_config)
    one_cro_fee = CROCoin("1", CRO_DENOM, local_test_network_config)
    msg_send_10_cro = MsgSend(
        from_address=alice_info["address"],
        to_address=bob_info["address"],
        amount=[ten_cro.protobuf_coin_message],
    )
    msg_send_20_cro = MsgSend(
        from_address=alice_info["address"],
        to_address=bob_info["address"],
        amount=[twnenty_cro.protobuf_coin_message],
    )

    tx = Transaction(
        chain_id=local_test_network_config.chain_id,
        from_wallets=[alice_wallet],
        msgs=[msg_send_10_cro],
        account_number=alice_account.account_number,
        fee=[one_cro_fee.protobuf_coin_message],
        client=client,
    ).append_message(msg_send_20_cro)

    sign_doc = tx.get_sign_doc()
    signature_alice = alice_wallet.sign(sign_doc.SerializeToString())
    signed_tx = tx.get_signed_tx([signature_alice])

    client.broadcast_transaction_block_mode(signed_tx.SerializeToString())

    alice_bal_aft = client.query_account_balance(alice_wallet.address)
    bob_bal_aft = client.query_account_balance(bob_wallet.address)
    alice_coin_aft = CROCoin(
        alice_bal_aft.balance.amount, alice_bal_aft.balance.denom, local_test_network_config
    )
    bob_coin_aft = CROCoin(
        bob_bal_aft.balance.amount, bob_bal_aft.balance.denom, local_test_network_config
    )

    assert alice_coin_aft == alice_coin_init.minus(ten_cro).minus(twnenty_cro).minus(one_cro_fee)
    assert bob_coin_aft == bob_coin_init.plus(ten_cro).plus(twnenty_cro)
