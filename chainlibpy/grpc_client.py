#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from dataclasses import dataclass
from typing import List, Optional

from google.protobuf.any_pb2 import Any as ProtoAny
from grpc import ChannelCredentials, RpcError, insecure_channel, secure_channel

from chainlibpy.generated.cosmos.crypto.multisig.keys_pb2 import LegacyAminoPubKey
from chainlibpy.generated.cosmos.crypto.multisig.v1beta1.multisig_pb2 import CompactBitArray, MultiSignature
from chainlibpy.generated.cosmos.auth.v1beta1.auth_pb2 import BaseAccount
from chainlibpy.generated.cosmos.auth.v1beta1.query_pb2 import QueryAccountRequest
from chainlibpy.generated.cosmos.auth.v1beta1.query_pb2_grpc import (
    QueryStub as AuthGrpcClient,
)
from chainlibpy.generated.cosmos.bank.v1beta1.query_pb2 import (
    QueryBalanceRequest,
    QueryBalanceResponse,
    QueryDenomMetadataRequest,
    QueryDenomMetadataResponse,
)
from chainlibpy.generated.cosmos.bank.v1beta1.query_pb2_grpc import (
    QueryStub as BankGrpcClient,
)
from chainlibpy.generated.cosmos.bank.v1beta1.tx_pb2 import MsgSend
from chainlibpy.generated.cosmos.base.v1beta1.coin_pb2 import Coin
from chainlibpy.generated.cosmos.crypto.secp256k1.keys_pb2 import PubKey as ProtoPubKey
from chainlibpy.generated.cosmos.tx.signing.v1beta1.signing_pb2 import SignMode
from chainlibpy.generated.cosmos.tx.v1beta1.service_pb2 import (
    BroadcastMode,
    BroadcastTxRequest,
    GetTxRequest,
    GetTxResponse,
)
from chainlibpy.generated.cosmos.tx.v1beta1.service_pb2_grpc import (
    ServiceStub as TxGrpcClient,
)
from chainlibpy.generated.cosmos.tx.v1beta1.tx_pb2 import (
    AuthInfo,
    Fee,
    ModeInfo,
    SignerInfo,
    Tx,
    TxBody,
)
from chainlibpy.transaction import sign_transaction
from chainlibpy.multisign.signature import MultiSignatureData, SingleSignatureV2



@dataclass
class NetworkConfig:
    grpc_endpoint: str
    chain_id: str
    address_prefix: str
    coin_denom: str
    coin_base_denom: str
    derivation_path: str


CRO_NETWORK = {
    "mainnet": NetworkConfig(
        grpc_endpoint="mainnet.crypto.org:9090",
        chain_id="crypto-org-chain-mainnet-1",
        address_prefix="cro",
        coin_denom="cro",
        coin_base_denom="basecro",
        derivation_path="m/44'/394'/0'/0/0",
    ),
    "testnet_croeseid": NetworkConfig(
        grpc_endpoint="testnet-croeseid-4.crypto.org:9090",
        chain_id="testnet-croeseid-4",
        address_prefix="tcro",
        coin_denom="tcro",
        coin_base_denom="basetcro",
        derivation_path="m/44'/1'/0'/0/0",
    ),
}


class GrpcClient:
    DEFAULT_GAS_LIMIT = 200000

    def __init__(
        self,
        network: NetworkConfig,
        account_number: int = None,
        credentials: ChannelCredentials = None,
    ) -> None:
        if credentials is None:
            channel = insecure_channel(network.grpc_endpoint)
        else:
            channel = secure_channel(network.grpc_endpoint, credentials)

        self.bank_client = BankGrpcClient(channel)
        self.tx_client = TxGrpcClient(channel)
        self.auth_client = AuthGrpcClient(channel)
        self.chain_id = network.chain_id
        self.account_number = account_number

    def query_bank_denom_metadata(self) -> QueryDenomMetadataResponse:
        res = self.bank_client.DenomMetadata(QueryDenomMetadataRequest(denom=self.network.coin_base_denom))
        return res

    def get_balance(self, address: str, denom: str) -> QueryBalanceResponse:
        res = self.bank_client.Balance(QueryBalanceRequest(address=address, denom=denom))
        return res

    def query_account_data(self, address: str) -> BaseAccount:
        account_response = self.auth_client.Account(QueryAccountRequest(address=address))
        account = BaseAccount()
        if account_response.account.Is(BaseAccount.DESCRIPTOR):
            account_response.account.Unpack(account)
        else:
            raise TypeError("Unexpected account type")
        return account

    def generate_tx(
        self,
        packed_msgs: List[ProtoAny],
        from_addresses: List[str],
        pub_keys: List[bytes],
        fee: Optional[List[Coin]] = None,
        memo: str = "",
        gas_limit: int = DEFAULT_GAS_LIMIT,
    ) -> Tx:
        accounts: List[BaseAccount] = []
        signer_infos: List[SignerInfo] = []
        for from_address, pub_key in zip(from_addresses, pub_keys):
            account = self.query_account_data(from_address)
            accounts.append(account)
            signer_infos.append(self._get_signer_info(account, pub_key))

        auth_info = AuthInfo(
            signer_infos=signer_infos,
            fee=Fee(amount=fee, gas_limit=gas_limit),
        )

        tx_body = TxBody()
        tx_body.memo = memo
        tx_body.messages.extend(packed_msgs)

        tx = Tx(body=tx_body, auth_info=auth_info)
        return tx

    def sign_tx(self, private_key: bytes, tx: Tx):
        sign_transaction(tx, private_key, self.chain_id, self.account_number)

    def get_packed_send_msg(self, from_address: str, to_address: str, amount: List[Coin]) -> ProtoAny:
        msg_send = MsgSend(from_address=from_address, to_address=to_address, amount=amount)
        send_msg_packed = ProtoAny()
        send_msg_packed.Pack(msg_send, type_url_prefix="/")

        return send_msg_packed

    def broadcast_tx(self, tx: Tx, wait_time: int = 10) -> GetTxResponse:
        tx_data = tx.SerializeToString()
        broad_tx_req = BroadcastTxRequest(tx_bytes=tx_data, mode=BroadcastMode.BROADCAST_MODE_SYNC)
        broad_tx_resp = self.tx_client.BroadcastTx(broad_tx_req)

        if broad_tx_resp.tx_response.code != 0:
            raw_log = broad_tx_resp.tx_response.raw_log
            raise RuntimeError(f"Transaction failed: {raw_log}")

        time.sleep(wait_time)

        tx_request = GetTxRequest(hash=broad_tx_resp.tx_response.txhash)
        tx_response = self.tx_client.GetTx(tx_request)

        return tx_response

    def bank_send(self, from_address: str, public_key: bytes, to_address: str, amount: List[Coin]) -> GetTxResponse:
        msg = self.get_packed_send_msg(
            from_address=from_address, to_address=to_address, amount=amount
        )

        tx = self.generate_tx([msg], [from_address], [public_key])
        self.sign_tx(tx)
        return self.broadcast_tx(tx)

    def _get_signer_info(self, from_acc: BaseAccount, pub_key: ProtoPubKey) -> SignerInfo:
        from_pub_key_packed = ProtoAny()
        from_pub_key_pb = ProtoPubKey(key=pub_key)
        from_pub_key_packed.Pack(from_pub_key_pb, type_url_prefix="/")

        # Prepare auth info
        single = ModeInfo.Single(mode=SignMode.SIGN_MODE_DIRECT)
        mode_info = ModeInfo(single=single)
        signer_info = SignerInfo(
            public_key=from_pub_key_packed,
            mode_info=mode_info,
            sequence=from_acc.sequence,
        )
        return signer_info

def get_muli_signer_info(sequence: int, multi_pubkey: LegacyAminoPubKey, bitarray: CompactBitArray) -> SignerInfo:
    multi_pubkey_packed = ProtoAny()
    multi_pubkey_packed.Pack(multi_pubkey, type_url_prefix="/")

    # Prepare auth info
    mode_infos = [ModeInfo.Single(mode=SignMode.SIGN_MODE_LEGACY_AMINO_JSON)] * multi_pubkey.threshold
    multi = ModeInfo.Multi(bitarray, mode_infos)
    mode_info = ModeInfo(multi=multi)
    signer_info = SignerInfo(
        public_key=multi_pubkey_packed,
        mode_info=mode_info,
        sequence=sequence,
    )
    return signer_info

def gen_multi_tx(
        packed_msgs: List[ProtoAny],
        multi_pubkey: LegacyAminoPubKey,
        signature_batch: List[SingleSignatureV2],
        sequence: int,
        fee: Optional[List[Coin]] = None,
        memo: str = "",
        gas_limit: int = 2000,
) -> Tx:
    def packed_proto_pubkey(pub_key: ProtoPubKey):
        from_pub_key_packed = ProtoAny()
        return from_pub_key_packed.Pack(pub_key, type_url_prefix="/")

    all_proto_pubkeys = [p for p in multi_pubkey.public_keys]
    n = len(signature_batch)
    multi_sign_data = MultiSignatureData(n)
    for sig_v2 in signature_batch:
        multi_sign_data.add_signature_v2(sig_v2, all_proto_pubkeys)

    signer_info = get_muli_signer_info(sequence, multi_pubkey, multi_sign_data.bit_array)
    signer_infos: List[SignerInfo] = []
    signer_infos.append(signer_info)
    auth_info = AuthInfo(
        signer_infos=signer_infos,
        fee=Fee(amount=fee, gas_limit=gas_limit),
    )

    tx_body = TxBody()
    tx_body.memo = memo
    tx_body.messages.extend(packed_msgs)
    multi_signature = MultiSignature(signatures=multi_sign_data.signatures)
    signatures = list()
    signatures.append(multi_signature)
    packed_pubkeys = [packed_proto_pubkey(p.pub_key) for p in signature_batch]
    tx = Tx(body=tx_body, auth_info=auth_info, public_keys=packed_pubkeys, signatures=signatures)
    return tx
