#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssl

import grpc

from chainlibpy.grpc_client import GrpcClient
from chainlibpy.wallet import Wallet

DENOM = "basetcro"
MNEMONIC_PHRASE = "first ... last"
CHAIN_ID = "testnet-croeseid-4"

SERVER_HOST = "testnet-croeseid-4.crypto.org"
SERVER_PORT = "9090"
GRPC_ENDPOINT = f"{SERVER_HOST}:{SERVER_PORT}"

DEFAULT_DERIVATION_PATH = "m/44'/1'/0'/0/0"
DEFAULT_BECH32_HRP = "tcro"


def example_with_certificate_file():
    wallet = Wallet(MNEMONIC_PHRASE, DEFAULT_DERIVATION_PATH, DEFAULT_BECH32_HRP)

    # 1. .cer certificate file could be obtained from the browser
    #    more details could be found here https://stackoverflow.com/questions/25940396/how-to-export-certificate-from-chrome-on-a-mac/59466184#59466184 # noqa501
    # 2. convert .cer file to .crt file
    #    `openssl x509 -inform DER -in cert.cer -out cert.crt``
    with open("./cert.crt", "rb") as f:
        creds = grpc.ssl_channel_credentials(f.read())

    client = GrpcClient(wallet, CHAIN_ID, GRPC_ENDPOINT, creds)

    from_address = wallet.address
    res = client.get_balance(from_address, DENOM)
    print(f"address {from_address} initial balance: {res.balance.amount}")


def example_with_certificate_request():
    wallet = Wallet(MNEMONIC_PHRASE, DEFAULT_DERIVATION_PATH, DEFAULT_BECH32_HRP)

    # if server does not use Server Name Indication (SNI), commented code below is enough:
    # creds = ssl.get_server_certificate((SERVER_HOST, SERVER_PORT))
    conn = ssl.create_connection((SERVER_HOST, SERVER_PORT))
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sock = context.wrap_socket(conn, server_hostname=SERVER_HOST)
    certificate = ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))
    creds = grpc.ssl_channel_credentials(str.encode(certificate))

    client = GrpcClient(wallet, CHAIN_ID, GRPC_ENDPOINT, creds)

    from_address = wallet.address
    res = client.get_balance(from_address, DENOM)
    print(f"address {from_address} initial balance: {res.balance.amount}")


if __name__ == "__main__":
    example_with_certificate_file()
    example_with_certificate_request()
