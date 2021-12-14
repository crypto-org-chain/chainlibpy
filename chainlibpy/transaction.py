#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import hashlib

import ecdsa

from chainlibpy.generated.cosmos.tx.v1beta1.tx_pb2 import SignDoc, Tx


def sign_transaction(
    tx: Tx,
    private_key: bytes,
    chain_id: str,
    account_number: int,
):
    sd = SignDoc()
    sd.body_bytes = tx.body.SerializeToString()
    sd.auth_info_bytes = tx.auth_info.SerializeToString()
    sd.chain_id = chain_id
    sd.account_number = account_number

    data_for_signing = sd.SerializeToString()

    signing_key = ecdsa.SigningKey.from_string(
        private_key, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256
    )
    signature = signing_key.sign_deterministic(
        data_for_signing, sigencode=ecdsa.util.sigencode_string_canonize
    )
    tx.signatures.extend([signature])
