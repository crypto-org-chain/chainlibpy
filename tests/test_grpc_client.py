import pytest
from google.protobuf.any_pb2 import Any

from chainlibpy.generated.cosmos.auth.v1beta1.auth_pb2 import BaseAccount
from chainlibpy.generated.cosmos.auth.v1beta1.query_pb2 import (
    QueryAccountRequest,
    QueryAccountResponse,
)
from chainlibpy.generated.cosmos.auth.v1beta1.query_pb2_grpc import (
    QueryServicer as AuthQueryServicer,
)
from chainlibpy.generated.cosmos.auth.v1beta1.query_pb2_grpc import (
    add_QueryServicer_to_server as add_auth,
)
from chainlibpy.generated.cosmos.bank.v1beta1.query_pb2 import (
    QueryBalanceRequest,
    QueryBalanceResponse,
)
from chainlibpy.generated.cosmos.bank.v1beta1.query_pb2_grpc import (
    QueryServicer as BankQueryServicer,
)
from chainlibpy.generated.cosmos.bank.v1beta1.query_pb2_grpc import (
    add_QueryServicer_to_server as add_bank,
)
from chainlibpy.generated.cosmos.base.v1beta1.coin_pb2 import Coin
from chainlibpy.generated.cosmos.tx.v1beta1.service_pb2_grpc import (
    ServiceServicer as TxServiceServicer,
)
from chainlibpy.generated.cosmos.tx.v1beta1.service_pb2_grpc import (
    add_ServiceServicer_to_server as add_tx,
)
from chainlibpy.grpc_client import GrpcClient
from chainlibpy.wallet import Wallet


class MockBankQueryServicer(BankQueryServicer):
    def Balance(self, request: QueryBalanceRequest, context) -> QueryBalanceResponse:
        if request.address == "cro1yj3fd8gxrqd2662p8ywp26t4hfws9p5n75xjum":
            return QueryBalanceResponse(balance=Coin(amount="100000000", denom="basecro"))


class MockAuthQueryServicer(AuthQueryServicer):
    def Account(self, request: QueryAccountRequest, context) -> QueryAccountResponse:
        if request.address == "cro1yj3fd8gxrqd2662p8ywp26t4hfws9p5n75xjum":
            acc = BaseAccount(account_number=1)
            any = Any()
            any.Pack(acc)
            return QueryAccountResponse(account=any)


class MockTxServiceServicer(TxServiceServicer):
    pass


@pytest.fixture(scope="module")
def mock_grpc_client(_grpc_server, grpc_addr):
    seed = "burst negative solar evoke traffic yard lizard next series foster seminar enter wrist captain bulb trap giggle country sword season shoot boy bargain deal"  # noqa 501
    wallet = Wallet(seed)

    add_bank(MockBankQueryServicer(), _grpc_server)
    add_auth(MockAuthQueryServicer(), _grpc_server)
    add_tx(MockTxServiceServicer(), _grpc_server)

    _grpc_server.add_insecure_port(grpc_addr)
    _grpc_server.start()

    yield GrpcClient(wallet, "chainmaind", grpc_addr)
    _grpc_server.stop(grace=None)


def test_get_balance(mock_grpc_client):
    balance = mock_grpc_client.get_balance("cro1yj3fd8gxrqd2662p8ywp26t4hfws9p5n75xjum", "basecro")
    assert balance == QueryBalanceResponse(balance=Coin(amount="100000000", denom="basecro"))
