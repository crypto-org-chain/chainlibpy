#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List, Optional

from chainlibpy.generated.common import (
    CosmosSdkMsg,
    CosmosSdkTxInfo,
    Network,
    SingleCoin,
)
from chainlibpy.grpc_client import GrpcClient
from chainlibpy.wallet import Wallet

DEFAULT_GAS_LIMIT = 200_000
ZERO_COIN = SingleCoin.BASE_CRO(0)


class Transaction:
    def __init__(
        self,
        chain_id: str,
        from_wallet: Wallet,
        msgs: List[CosmosSdkMsg],
        account_number: int,
        client: "GrpcClient",
        gas_limit: int = DEFAULT_GAS_LIMIT,
        fee: SingleCoin = ZERO_COIN,
        memo: str = "",
        timeout_height: Optional[int] = None,
    ) -> None:
        """Transaction class to prepare unsigned transaction and generate
        signed transaction with signatures.

        Args:
            chain_id (str): chain id this transaction targets

            from_wallet (Wallet): wallet for the authorization
            related content of the transaction

            msgs (List[CosmosSdkMsg]): messages to be included in this transaction

            account_number (int): account number of the account in state

            client (GrpcClient): GrpcClient object to connect to chain

            gas_limit (int, optional): maximum gas can be used in transaction processing.
            Defaults to DEFAULT_GAS_LIMIT.

            fee (SingleCoin): amount of coins to be paid as a fee.
            Defaults to zero CRO.

            memo (str, optional): note to be added to the transaction. Defaults to "".

            timeout_height (int, optional): this transaction will not be processed
            after timeout height. Defaults to None.
        """
        self._chain_id = chain_id
        self._msgs = msgs
        self._fee = fee
        self._from_wallet = from_wallet
        self._memo = memo
        self._timeout_height = timeout_height
        self._account_number = account_number
        self._gas_limit = gas_limit
        self._client = client
        timeout = 0
        if timeout_height is not None:
            timeout = timeout_height
        self._tx_info = CosmosSdkTxInfo(
            account_number,
            0,
            gas_limit,
            fee,
            timeout,
            memo,
            Network.OTHER(chain_id, 394, "cro"),
        )

    def append_message(self, msg: CosmosSdkMsg) -> "Transaction":
        """Append a message to this transaction.

        Args:
            msg (CosmosSdkMsg): a message to be included in this transaction

        Returns:
            Transaction: transaction object with newly added messages
        """
        self._msgs.append(msg)

        return self

    @property
    def signed_tx(self) -> bytes:
        account = self._client.query_account(self._from_wallet.address)
        self._tx_info.sequence_number = account.sequence
        return self._from_wallet.sign_tx(self._tx_info, self._msgs)
