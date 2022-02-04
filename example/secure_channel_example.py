#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import ssl

import grpc

from chainlibpy import CRO_NETWORK, GrpcClient


def example_with_certificate_file():
    # 1. .cer certificate file could be obtained from the browser
    #    more details could be found here https://stackoverflow.com/questions/25940396/how-to-export-certificate-from-chrome-on-a-mac/59466184#59466184 # noqa: 501
    # 2. convert .cer file to .crt file
    #    `openssl x509 -inform DER -in cert.cer -out cert.crt`
    with open("./cert.crt", "rb") as f:
        creds = grpc.ssl_channel_credentials(f.read())

    client = GrpcClient(CRO_NETWORK["testnet_croeseid"], creds)

    print(client.query_bank_denom_metadata(CRO_NETWORK["testnet_croeseid"].coin_base_denom))


def example_with_certificate_request():
    (server_host, server_port) = CRO_NETWORK["testnet_croeseid"].grpc_endpoint.split(":")

    # if server does not use Server Name Indication (SNI), commented code below is enough:
    # creds = ssl.get_server_certificate((SERVER_HOST, SERVER_PORT))
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    with socket.create_connection((server_host, int(server_port))) as sock:
        with context.wrap_socket(sock, server_hostname=server_host) as ssock:
            certificate_DER = ssock.getpeercert(True)

    if certificate_DER is None:
        raise RuntimeError("no certificate returned from server")

    certificate_PEM = ssl.DER_cert_to_PEM_cert(certificate_DER)
    creds = grpc.ssl_channel_credentials(str.encode(certificate_PEM))

    client = GrpcClient(CRO_NETWORK["testnet_croeseid"], creds)

    print(client.query_bank_denom_metadata(CRO_NETWORK["testnet_croeseid"].coin_base_denom))


if __name__ == "__main__":
    example_with_certificate_file()
    example_with_certificate_request()
