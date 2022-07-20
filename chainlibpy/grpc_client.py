#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from chainlibpy.generated.common import (
    BalanceApiVersion,
    CosmosSdkClient,
    DenomMetadata,
    RawRpcAccountStatus,
    RawRpcBalance,
    TxBroadcastMode,
    TxBroadcastResult,
)


@dataclass
class NetworkConfig:
    grpc_endpoint: str
    tendermint_rpc: str
    rest_api: str
    chain_id: str
    address_prefix: str
    coin_denom: str
    coin_base_denom: str
    exponent: int
    derivation_path: str


CRO_NETWORK = {
    "mainnet": NetworkConfig(
        grpc_endpoint="https://mainnet.crypto.org:9090",
        tendermint_rpc="https://mainnet.crypto.org:443",
        rest_api="https://mainnet.crypto.org:1317",
        chain_id="crypto-org-chain-mainnet-1",
        address_prefix="cro",
        coin_denom="cro",
        coin_base_denom="basecro",
        exponent=8,
        derivation_path="m/44'/394'/0'/0/0",
    ),
    "testnet_croeseid": NetworkConfig(
        grpc_endpoint="https://testnet-croeseid-4.crypto.org:9090",
        tendermint_rpc="https://testnet-croeseid-4.crypto.org:443",
        rest_api="https://testnet-croeseid-4.crypto.org:1317",
        chain_id="testnet-croeseid-4",
        address_prefix="tcro",
        coin_denom="tcro",
        coin_base_denom="basetcro",
        exponent=8,
        derivation_path="m/44'/1'/0'/0/0",
    ),
}

DEFAULT_MODE = TxBroadcastMode.COMMIT()


class GrpcClient:
    def __init__(
        self,
        network: NetworkConfig,
    ) -> None:
        self.chain_id = network.chain_id
        self.network = network
        self.client = CosmosSdkClient(
            network.tendermint_rpc, network.rest_api, BalanceApiVersion.NEW, network.grpc_endpoint
        )

    def query_bank_denom_metadata(self, denom: str) -> DenomMetadata:
        """Queries metadata of a given coin denomination.

        Args:
            denom (str): the native coin denomation

        Returns:
            DenomMetadata: information about the queried denomination
        """
        res = self.client.get_denom_metadata(denom)
        return res

    def query_account_balance(self, address: str) -> RawRpcBalance:
        """Queries the balance of an address in base denomination.

        Args:
            address (str): address to query balance

        Returns:
            RawRpcBalance: cosmos.bank.v1beta1.QueryBalanceResponse message

            Access `amount` by `.amount`

            Access `denom` by `.denom`
        """
        return self.client.get_account_balance(address, self.network.coin_base_denom)

    def query_account(self, address: str) -> RawRpcAccountStatus:
        """Queries the account information.

        Args:
            address (str): address to query account

        Raises:
            TypeError: account associated with address is not `BaseAccount`

        Returns:
            RawRpcAccountStatus: cosmos.auth.v1beta1.BaseAccount message

            Access `account_number` by `.account_number`

            Access `sequence` by `.sequence`
        """
        account_response = self.client.get_account_details(address)
        if account_response.is_error_response():
            raise TypeError("Error response: {}".format(account_response))
        return account_response.account

    def broadcast_transaction(
        self, tx_byte: bytes, mode: TxBroadcastMode = DEFAULT_MODE
    ) -> TxBroadcastResult:
        """Broadcasts raw transaction in a mode.

        sync mode: client waits for a CheckTx execution response only

        async mode: client returns immediately

        block mode(default): client waits for the tx to be committed in a block

        Args:
            tx_byte (bytes): raw transaction
            mode (TxBroadcastMode): broadcast mode. Defaults to "TxBroadcastMode.COMMIT".

        Returns:
            BroadcastTxResponse: a subset of cosmos.tx.v1beta1.service_pb2.BroadcastTxResponse
        """
        return self.client.broadcast_tx(tx_byte, mode)
