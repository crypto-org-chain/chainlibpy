import time
from pathlib import Path

import requests
import yaml
from google.protobuf.any_pb2 import Any as ProtoAny
from pystarport.cluster import ClusterCLI, init_cluster, interact, start_cluster
from pystarport.ports import api_port
from pystarport.proto_python.api_util import ApiUtil

from chainlibpy.amino import Coin, StdFee
from chainlibpy.amino.message import MsgSend
from chainlibpy.amino.transaction import Transaction
from chainlibpy.generated.cosmos.base.v1beta1.coin_pb2 import Coin as ProtoCoin
from chainlibpy.generated.cosmos.crypto.multisig.keys_pb2 import LegacyAminoPubKey
from chainlibpy.generated.cosmos.crypto.secp256k1.keys_pb2 import PubKey as ProtoPubKey
from chainlibpy.grpc_client import GrpcClient, gen_multi_tx, get_packed_send_msg
from chainlibpy.multisign.signature import SingleSignatureV2
from chainlibpy.wallet import Wallet


def packed_to_any(m):
    packed = ProtoAny()
    packed.Pack(m, type_url_prefix="/")
    return packed


class ChainMainClient(object):
    '''
    we use pystarport to create the IBC env
    need to install hermes: https://github.com/informalsystems/ibc-rs/releases
    '''

    def __init__(self, data_root=Path("/tmp/data"), config_file="config.yaml", chain_id="chain_id_test"):
        self.data_root = data_root
        self.config_file = config_file
        self.chain_id = chain_id

    @property
    def cluster(self):
        config = yaml.safe_load(open(self.config_file))
        clis = {}
        for key in config:
            if key == "relayer":
                continue
            chain_id = key
            clis[chain_id] = ClusterCLI(self.data_root, chain_id=chain_id)
        return clis[self.chain_id]

    def url_base(self, index=0):
        cli = self.cluster
        port = api_port(cli.base_port(index))
        return "http://127.0.0.1:{}".format(port)

    @property
    def api(self):
        index = 0
        cli = self.cluster
        port = api_port(cli.base_port(index))
        return ApiUtil(port)

    def get_balance(self, address):
        url_base = self.url_base(index=0)
        url_balance = f"{url_base}/cosmos/bank/v1beta1/balances/{address}"
        print(url_balance)
        response = requests.get(url_balance)
        balance = int(response.json()["balances"][0]["amount"])
        return balance

    def get_account_info(self, address):
        account_info = self.api.account_info(address)
        account_num = int(account_info["account_num"])
        sequence = int(account_info["sequence"])
        return account_num, sequence

    def send_tx(self, data):
        url_base = self.url_base()
        print(url_base)
        url = f"{url_base}/cosmos/tx/v1beta1/txs"
        response = requests.post(url, json=data)
        return response

    def start(self):
        '''
        after start the tasks, you can use `supervisorctl -c task.ini` to see the status of each program
        '''
        interact(f"rm -r {self.data_root}; mkdir -p {self.data_root}", ignore_error=True)
        data_dir = Path(self.data_root)
        init_cluster(data_dir, "config.yaml", 26650)
        start_cluster(data_dir)


# def get_multi_addr(multi_wallet_name: str):
#     client = ChainMainClient()
#     cluster = client.cluster
#     import pdb; pdb.set_trace()
#     return cluster.address(multi_wallet_name)


# the wallets which create the multi wallet
SEED_0 = "hurry exist clerk safe aware anchor brush run dentist come surge frame tired economy school grief volcano enforce word alpha liar clever sure taxi"
SEED_1 = "repeat life corn cliff tragic merry zoo saddle fuel shove column pulp decorate forward rabbit ocean agent snack gaze mansion when wood grab pear"
MULTI_WALLET = "multi_wallet"


def prepare(multi_wallet_name: str):
    """
    """
    # 1. create multi wallet
    client = ChainMainClient()
    cluster = client.cluster
    cluster.make_multisig(multi_wallet_name, "msigner0", "msigner1")
    multi_addr = cluster.address(multi_wallet_name)

    # 2. send some coin to multi wallet
    wallet_0 = Wallet(SEED_0)
    cluster.transfer(wallet_0.address, multi_addr, "500basecro")
    time.sleep(10)
    balance = client.get_balance(multi_addr)
    print("multi address balance: ", balance)
    return multi_addr


def main():
    chain_id = "chain_id_test"
    wallet_0 = Wallet(SEED_0)
    wallet_1 = Wallet(SEED_1)
    chain_maind_client = ChainMainClient(chain_id=chain_id)
    # multi_wallet_name = "multi_wallet"
    # multi_address = prepare(multi_wallet_name)
    multi_address = "cro15ejy7v88xarw5ce29t2rsve3kxn8d7ug44jayh"
    to_address = "cro1hk220qwxp0c8m3pzazardmmfv8y0mg7ukdnn37"

    # print multi wallet balance
    balance = chain_maind_client.get_balance(multi_address)
    print("multi address balance: ", balance)

    fee = StdFee(gas="2000", amount=[])
    # multi_wallet_addr = get_multi_addr(multi_wallet_name)
    # account_num, sequence = chain_maind_client.get_account_info(multi_wallet_addr)

    grpc_client = GrpcClient(chain_id, "basecro", "0.0.0.0:26653", None)
    res = grpc_client.get_balance(multi_address)
    print(f"get multi address balance: {res.balance.amount}")
    account_info = grpc_client.query_account_data(multi_address)
    account_num = account_info.account_num
    sequence = account_info
    print(f"account_num {account_num}, sequence: {sequence}")
    # account_num, sequence = 12, 0

    amount = "100"
    msg = MsgSend(from_address=multi_address, to_address=to_address, amount=[Coin(amount)])

    # first make two single amino transaction, and create single_sig_v2
    sig_batch = list()
    threshold = 2

    any_pubkeys = [packed_to_any(ProtoPubKey(key=w.public_key)) for w in [wallet_0, wallet_1]]
    multi_pubkey = LegacyAminoPubKey(threshold=threshold, public_keys=any_pubkeys)
    for index, wallet in enumerate([wallet_0, wallet_1]):
        tx = Transaction(
            wallet=wallet,
            account_num=account_num,
            sequence=sequence,
            chain_id=chain_id,
            fee=fee,
            multi_sign_address=multi_address
        )
        tx.add_msg(msg)
        single_sig_v2 = SingleSignatureV2(wallet.public_key, sequence, tx.sign())
        sig_batch.append(single_sig_v2)

    amount = [ProtoCoin(amount="10000", denom="basecro")]
    msg = get_packed_send_msg(multi_address, to_address, amount)
    tx = gen_multi_tx(
        [msg],
        multi_pubkey,
        sig_batch,
        sequence,
    )
    response = grpc_client.broadcast_tx(tx)
    print(f"send tx response: {response}")

if __name__ == "__main__":
    main()
