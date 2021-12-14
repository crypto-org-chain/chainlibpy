#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from typing import List, Optional

from google.protobuf.any_pb2 import Any as ProtoAny
from grpc import insecure_channel

from chainlibpy.generated.cosmos.auth.v1beta1.auth_pb2 import BaseAccount
from chainlibpy.generated.cosmos.auth.v1beta1.query_pb2 import QueryAccountRequest
from chainlibpy.generated.cosmos.auth.v1beta1.query_pb2_grpc import (
    QueryStub as AuthGrpcClient,
)
from chainlibpy.generated.cosmos.bank.v1beta1.query_pb2 import (
    QueryBalanceRequest,
    QueryBalanceResponse,
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
from chainlibpy.wallet import Wallet


class GrpcClient:
    DEFAULT_GAS_LIMIT = 200000

    def __init__(self, wallet: Wallet, chain_id: str, grpc_endpoint: str) -> None:
        channel = insecure_channel(grpc_endpoint)

        self.bank_client = BankGrpcClient(channel)
        self.tx_client = TxGrpcClient(channel)
        self.auth_client = AuthGrpcClient(channel)
        self.wallet = wallet
        self.chain_id = chain_id
        account = self.query_account_data(self.wallet.address)
        self.account_number = account.account_number

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

    def sign_tx(self, tx: Tx):
        sign_transaction(tx, self.wallet.private_key, self.chain_id, self.account_number)

    def get_packed_send_msg(
        self, from_address: str, to_address: str, amount: List[Coin]
    ) -> ProtoAny:
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

    def bank_send(self, to_address: str, amount: List[Coin]) -> GetTxResponse:
        msg = self.get_packed_send_msg(
            from_address=self.wallet.address, to_address=to_address, amount=amount
        )

        tx = self.generate_tx([msg], [self.wallet.address], [self.wallet.public_key])
        self.sign_tx(tx)
        return self.broadcast_tx(tx)

    def _get_signer_info(self, from_acc: BaseAccount, pub_key: bytes) -> SignerInfo:
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
