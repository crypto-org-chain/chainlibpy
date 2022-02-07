#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Literal, Optional

from grpc import ChannelCredentials, insecure_channel, secure_channel

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
from chainlibpy.generated.cosmos.tx.v1beta1.service_pb2 import (
    BroadcastMode,
    BroadcastTxRequest,
)
from chainlibpy.generated.cosmos.tx.v1beta1.service_pb2_grpc import (
    ServiceStub as TxGrpcClient,
)


@dataclass
class NetworkConfig:
    grpc_endpoint: str
    chain_id: str
    address_prefix: str
    coin_denom: str
    coin_base_denom: str
    exponent: int
    derivation_path: str


CRO_NETWORK = {
    "mainnet": NetworkConfig(
        grpc_endpoint="mainnet.crypto.org:9090",
        chain_id="crypto-org-chain-mainnet-1",
        address_prefix="cro",
        coin_denom="cro",
        coin_base_denom="basecro",
        exponent=8,
        derivation_path="m/44'/394'/0'/0/0",
    ),
    "testnet_croeseid": NetworkConfig(
        grpc_endpoint="testnet-croeseid-4.crypto.org:9090",
        chain_id="testnet-croeseid-4",
        address_prefix="tcro",
        coin_denom="tcro",
        coin_base_denom="basetcro",
        exponent=8,
        derivation_path="m/44'/1'/0'/0/0",
    ),
}


class GrpcClient:
    def __init__(
        self,
        network: NetworkConfig,
        credentials: Optional[ChannelCredentials] = None,
    ) -> None:
        if credentials is None:
            channel = insecure_channel(network.grpc_endpoint)
        else:
            channel = secure_channel(network.grpc_endpoint, credentials)

        self.bank_client = BankGrpcClient(channel)
        self.tx_client = TxGrpcClient(channel)
        self.auth_client = AuthGrpcClient(channel)
        self.chain_id = network.chain_id
        self.network = network

    def query_bank_denom_metadata(self, denom: str) -> QueryDenomMetadataResponse:
        """Queries metadata of a given coin denomination.

        Args:
            denom (str): raw transaction

        Returns:
            QueryDenomMetadataResponse: cosmos.bank.v1beta1.QueryDenomMetadataResponse message
        """
        res = self.bank_client.DenomMetadata(QueryDenomMetadataRequest(denom=denom))
        return res

    def query_account_balance(self, address: str) -> QueryBalanceResponse:
        """Queries the balance of an address in base denomination.

        Args:
            address (str): address to query balance

        Returns:
            QueryBalanceResponse: cosmos.bank.v1beta1.QueryBalanceResponse message

            Access `amount` by `.balance.amount`

            Access `denom` by `.balance.denom`
        """
        res = self.bank_client.Balance(
            QueryBalanceRequest(address=address, denom=self.network.coin_base_denom)
        )
        return res

    def query_account(self, address: str) -> BaseAccount:
        """Queries the account information.

        Args:
            address (str): address to query account

        Raises:
            TypeError: account associated with address is not `BaseAccount`

        Returns:
            BaseAccount: cosmos.auth.v1beta1.BaseAccount message

            Access `account_number` by `.account_number`

            Access `sequence` by `.sequence`
        """
        account_response = self.auth_client.Account(QueryAccountRequest(address=address))
        account = BaseAccount()
        if account_response.account.Is(BaseAccount.DESCRIPTOR):
            account_response.account.Unpack(account)
        else:
            raise TypeError("Unexpected account type")
        return account

    def broadcast_transaction(
        self, tx_byte: bytes, mode: Literal["sync", "async", "block"] = "block"
    ) -> None:
        """Broadcasts raw transaction in a mode.

        sync mode: client waits for a CheckTx execution response only

        async mode: client returns immediately

        block mode(default): client waits for the tx to be committed in a block

        Args:
            tx_byte (bytes): raw transaction
            mode (Literal[, optional): broadcast mode. Defaults to "block".

        Raises:
            TypeError: mode is not one of "sync", "async" or "block"
        """
        if mode == "sync":
            _mode = BroadcastMode.BROADCAST_MODE_SYNC
        elif mode == "async":
            _mode = BroadcastMode.BROADCAST_MODE_ASYNC
        elif mode == "block":
            _mode = BroadcastMode.BROADCAST_MODE_BLOCK
        else:
            raise TypeError("Unexcepted mode, should be [sync, async, block]")

        self.tx_client.BroadcastTx(BroadcastTxRequest(tx_bytes=tx_byte, mode=_mode))
