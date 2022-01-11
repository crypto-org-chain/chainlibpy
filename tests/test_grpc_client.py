import ssl

import grpc
import pytest

from chainlibpy import CRO_NETWORK, GrpcClient, NetworkConfig, Wallet


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
