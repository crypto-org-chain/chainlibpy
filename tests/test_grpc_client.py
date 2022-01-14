import ssl

import grpc
import pytest

from chainlibpy import CRO_NETWORK, GrpcClient, NetworkConfig, Wallet

from .utils import ALICE, get_blockchain_account_info, get_predefined_account_coins


@pytest.mark.parametrize("network_config", CRO_NETWORK.values())
def test_network_config(network_config: "NetworkConfig"):
    wallet = Wallet.new(path=network_config.derivation_path, hrp=network_config.address_prefix)

    (server_host, server_port) = network_config.grpc_endpoint.split(":")

    conn = ssl.create_connection((server_host, server_port))
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sock = context.wrap_socket(conn, server_hostname=server_host)
    certificate = ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))
    creds = grpc.ssl_channel_credentials(str.encode(certificate))

    client = GrpcClient(wallet, network_config, creds)

    assert (
        client.query_bank_denom_metadata(network_config.coin_base_denom).metadata.base
        == network_config.coin_base_denom
    )


# TODO
# Note: temporary test case to test newly added fixtures and local test environment
def test_test_environment(blockchain_config_dict, blockchain_accounts, local_test_network_config):
    alice_coin = get_predefined_account_coins(blockchain_config_dict, ALICE)
    print(alice_coin)

    alice_account = get_blockchain_account_info(blockchain_accounts, ALICE)
    print(alice_account)

    wallet_default_derivation = Wallet(alice_account["mnemonic"])
    assert wallet_default_derivation.address == alice_account["address"]

    client = GrpcClient(wallet_default_derivation, local_test_network_config)
    print(client.get_balance(wallet_default_derivation.address, "basecro"))
