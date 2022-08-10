#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from chainlibpy import CRO_NETWORK, GrpcClient


def example_with_tls():
    client = GrpcClient(CRO_NETWORK["testnet_croeseid"])

    print(client.query_bank_denom_metadata(CRO_NETWORK["testnet_croeseid"].coin_base_denom))


if __name__ == "__main__":
    example_with_tls()
