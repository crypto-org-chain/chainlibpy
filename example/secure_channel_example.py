#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssl

import grpc

from chainlibpy.grpc_client import CRO_NETWORK, GrpcClient
from chainlibpy.wallet import Wallet

MNEMONIC_PHRASE = "first ... last"


def example_with_certificate_file():
    config = CRO_NETWORK["testnet_croeseid"]
    wallet = Wallet(MNEMONIC_PHRASE, config.derivation_path, config.address_prefix)

    # 1. .cer certificate file could be obtained from the browser
    #    more details could be found here https://stackoverflow.com/questions/25940396/how-to-export-certificate-from-chrome-on-a-mac/59466184#59466184 # noqa501
    # 2. convert .cer file to .crt file
    #    `openssl x509 -inform DER -in cert.cer -out cert.crt``
    with open("./cert.crt", "rb") as f:
        creds = grpc.ssl_channel_credentials(f.read())
    client = GrpcClient(config, creds)
    from_address = wallet.address
    res = client.get_balance(from_address)
    print(f"address {from_address} initial balance: {res.balance.amount}")


def example_with_certificate_request():
    config = CRO_NETWORK["testnet_croeseid"]
    wallet = Wallet(MNEMONIC_PHRASE, config.derivation_path, config.address_prefix)

    # if server does not use Server Name Indication (SNI), commented code below is enough:
    # creds = ssl.get_server_certificate((SERVER_HOST, SERVER_PORT))
    (server_host, server_port) = config.grpc_endpoint.split(":")
    conn = ssl.create_connection((server_host, server_port))
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sock = context.wrap_socket(conn, server_hostname=server_host)
    certificate = ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))
    creds = grpc.ssl_channel_credentials(str.encode(certificate))
    client = GrpcClient(config, creds)
    from_address = wallet.address
    res = client.get_balance(from_address)
    print(f"address {from_address} initial balance: {res.balance.amount}")


if __name__ == "__main__":
    example_with_certificate_file()
    example_with_certificate_request()
