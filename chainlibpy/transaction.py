#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List, Optional

from chainlibpy.multisign.signature import MultiSignatureData, SingleSignatureV2
from google.protobuf import any_pb2, message
from google.protobuf.any_pb2 import Any as ProtoAny

from chainlibpy.generated.cosmos.base.v1beta1.coin_pb2 import Coin
from chainlibpy.generated.cosmos.bank.v1beta1.tx_pb2 import MsgSend
from chainlibpy.generated.cosmos.crypto.secp256k1.keys_pb2 import PubKey
from chainlibpy.generated.cosmos.crypto.multisig.keys_pb2 import LegacyAminoPubKey
from chainlibpy.generated.cosmos.tx.signing.v1beta1.signing_pb2 import SignMode
from chainlibpy.generated.cosmos.crypto.multisig.v1beta1.multisig_pb2 import (
    CompactBitArray as ProtoCompactBitArray, MultiSignature,
)
from chainlibpy.generated.cosmos.tx.v1beta1.tx_pb2 import (
    AuthInfo,
    Fee,
    ModeInfo,
    SignDoc,
    SignerInfo,
    Tx,
    TxBody,
)
from chainlibpy.grpc_client import GrpcClient
from chainlibpy.utils import pack_to_any_message
from chainlibpy.wallet import Wallet

DEFAULT_GAS_LIMIT = 200_000


class Transaction:
    def __init__(
            self,
            chain_id: str,
            from_wallets: List[Wallet],
            msgs: List[message.Message],
            account_number: int,
            client: "GrpcClient",
            gas_limit: int = DEFAULT_GAS_LIMIT,
            fee: Optional[List[Coin]] = None,
            memo: str = "",
            timeout_height: Optional[int] = None,
    ) -> None:
        """Transaction class to prepare unsigned transaction and generate
        signed transaction with signatures.

        Args:
            chain_id (str): chain id this transaction targets

            from_wallets (List[Wallet]): wallets for the authorization
            related content of the transaction

            msgs (List[message.Message]): messages to be included in this transaction

            account_number (int): account number of the account in state

            client (GrpcClient): GrpcClient object to connect to chain

            gas_limit (int, optional): maximum gas can be used in transaction processing.
            Defaults to DEFAULT_GAS_LIMIT.

            fee (Optional[List[Coin]], optional): amount of coins to be paid as a fee.
            Defaults to None.

            memo (str, optional): note to be added to the transaction. Defaults to "".

            timeout_height (int, optional): this transaction will not be processed
            after timeout height. Defaults to None.
        """
        self._chain_id = chain_id
        self._packed_msgs = self._pack_msgs_to_any_msgs(msgs)
        self._fee = fee
        self._from_wallets = from_wallets
        self._memo = memo
        self._timeout_height = timeout_height
        self._account_number = account_number
        self._gas_limit = gas_limit
        self._client = client

    def _pack_msgs_to_any_msgs(self, msgs: List[message.Message]) -> List[any_pb2.Any]:
        return [pack_to_any_message(msg) for msg in msgs]

    def append_message(self, *msgs: message.Message) -> "Transaction":
        """Append more messages in this transaction.

        Args:
            *msgs (message.Message): messages to be included in this transaction

        Returns:
            Transaction: transaction object with newly added messages
        """
        self._packed_msgs.extend(self._pack_msgs_to_any_msgs(list(msgs)))

        return self

    def set_signatures(self, *signatures: bytes) -> "Transaction":
        """Set signatures for this transaction.

        Args:
            *signatures (bytes): signatures to be included in this transaction

        Returns:
            Transaction: transaction object with newly added signatures
        """

        self._signatures = list(signatures)

        return self

    @property
    def tx_body(self) -> TxBody:
        return TxBody(messages=self._packed_msgs, memo=self._memo)

    @property
    def auth_info(self) -> AuthInfo:
        signer_infos = []
        for wallet in self._from_wallets:
            # query account to get the latest account.sequence
            account = self._client.query_account(wallet.address)

            signer_info = SignerInfo(
                public_key=pack_to_any_message(PubKey(key=wallet.public_key)),
                mode_info=ModeInfo(single=ModeInfo.Single(mode=SignMode.SIGN_MODE_DIRECT)),
                sequence=account.sequence,
            )

            signer_infos.append(signer_info)

        return AuthInfo(
            signer_infos=signer_infos, fee=Fee(amount=self._fee, gas_limit=self._gas_limit)
        )

    @property
    def sign_doc(self) -> SignDoc:
        return SignDoc(
            body_bytes=self.tx_body.SerializeToString(),
            auth_info_bytes=self.auth_info.SerializeToString(),
            chain_id=self._chain_id,
            account_number=self._account_number,
        )

    @property
    def signed_tx(self) -> Tx:
        if self._signatures is None:
            raise TypeError("Set signatures first before getting signed_tx")

        return Tx(body=self.tx_body, auth_info=self.auth_info, signatures=self._signatures)


def gen_muli_signer_info(
        sequence: int,
        multi_pubkey: LegacyAminoPubKey,
        bitarray: ProtoCompactBitArray
) -> SignerInfo:
    multi_pubkey_packed = ProtoAny().Pack(multi_pubkey, type_url_prefix="/")

    # Prepare auth info
    signal_mode_info = ModeInfo(single=ModeInfo.Single(mode=SignMode.SIGN_MODE_LEGACY_AMINO_JSON))
    mode_infos = [signal_mode_info] * multi_pubkey.threshold
    multi = ModeInfo.Multi(bitarray=bitarray, mode_infos=mode_infos)
    mode_info = ModeInfo(multi=multi)
    signer_info = SignerInfo(
        public_key=multi_pubkey_packed,
        mode_info=mode_info,
        sequence=sequence,
    )
    return signer_info


def gen_packed_send_msg(from_address: str, to_address: str, amount: List[Coin]) -> ProtoAny:
    msg_send = MsgSend(from_address=from_address, to_address=to_address, amount=amount)
    send_msg_packed = ProtoAny()
    send_msg_packed.Pack(msg_send, type_url_prefix="/")

    return send_msg_packed


def gen_multi_signer_info(
        sequence: int,
        multi_pubkey: LegacyAminoPubKey,
        bitarray: ProtoCompactBitArray
) -> SignerInfo:
    multi_pubkey_packed = ProtoAny()
    multi_pubkey_packed.Pack(multi_pubkey, type_url_prefix="/")

    # Prepare auth info
    signal_mode_info = ModeInfo(single=ModeInfo.Single(mode=SignMode.SIGN_MODE_LEGACY_AMINO_JSON))
    mode_infos = [signal_mode_info] * multi_pubkey.threshold
    multi = ModeInfo.Multi(bitarray=bitarray, mode_infos=mode_infos)
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
    if multi_pubkey.threshold > len(signature_batch):
        raise Exception("single signatures should >= threshold")

    all_proto_pubkeys = [p for p in multi_pubkey.public_keys]
    n = len(signature_batch)
    multi_sign_data = MultiSignatureData(n)
    for sig_v2 in signature_batch:
        multi_sign_data.add_single_sig_v2(sig_v2, all_proto_pubkeys)

    signer_info = gen_muli_signer_info(sequence, multi_pubkey, multi_sign_data.bit_array)
    signer_infos = list()
    signer_infos.append(signer_info)
    auth_info = AuthInfo(
        signer_infos=signer_infos,
        fee=Fee(amount=fee, gas_limit=gas_limit),
    )

    tx_body = TxBody()
    tx_body.memo = memo
    tx_body.messages.extend(packed_msgs)
    multi_signature = MultiSignature(signatures=multi_sign_data.signatures)

    tx = Tx(body=tx_body, auth_info=auth_info, signatures=[multi_signature.SerializeToString()])
    return tx
