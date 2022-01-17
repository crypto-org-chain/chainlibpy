import json
from pathlib import Path
import requests
import yaml
from pystarport.cluster import (ClusterCLI, find_account, init_cluster,
                                interact, start_cluster)
from pystarport.ports import api_port
from pystarport.proto_python.api_util import ApiUtil
from chainlibpy.wallet import Wallet
from chainlibpy.amino.transaction import Transaction
from chainlibpy.amino import Coin, StdFee
from chainlibpy.amino.message import MsgSend
from chainlibpy.multisign.signature import SingleSignatureV2
from chainlibpy.grpc_client import gen_multi_tx, GrpcClient
from chainlibpy.generated.cosmos.crypto.secp256k1.keys_pb2 import PubKey as ProtoPubKey
from chainlibpy.grpc_client import Coin as ProtoCoin
from chainlibpy.generated.cosmos.crypto.multisig.keys_pb2 import LegacyAminoPubKey
from chainlibpy.amino.basic import DEFAULT_BECH32_HRP_BASE
from google.protobuf.any_pb2 import Any as ProtoAny


def packed_to_any(m):
    packed = ProtoAny()
    packed.Pack(m, type_url_prefix="/")
    return packed


class ChainMainClient():
    '''
    we use pystarport to create the IBC env
    need to install hermes: https://github.com/informalsystems/ibc-rs/releases
    '''
    def __init__(self, data_root=Path("/tmp/data"), config_file="config.yaml"):
        self.data_root = data_root
        self.config_file = config_file
        self.chain_id = "chain_id_test"

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
        data_path = "/tmp/dadta"
        interact(f"rm -r {data_path}; mkdir -p {data_path}", ignore_error=True)
        data_dir = Path("/tmp/data")
        init_cluster(data_dir, "config.yaml", 26650)
        start_cluster(data_dir)

def find_account(data_dir, chain_id, name):
    accounts = json.load((data_dir / chain_id / "accounts.json").open())
    return next(acct for acct in accounts if acct["name"] == name)

def get_multi_addr(multi_wallet_name: str):
    r = ChainMainClient()
    cluster = r.cluster
    return cluster.address(multi_wallet_name)

def prepare(chain_maind_client: ChainMainClient, multi_wallet_name: str):
    """
    1. create multi wallet
    2. send some coin to multi wallet
    """


    multi_wallet_addr = get_multi_addr(multi_wallet_name)
    balance = chain_maind_client.get_balance(multi_wallet_addr)
    print("multi address balance: ", balance)

def main():
    chain_id = "chain_id_test"
    multi_wallet_name = "multi_wallet"
    chain_maind_client = ChainMainClient()

    seed_0 = find_account(chain_maind_client.data_root, chain_id, "msigner0")["mnemonic"]
    print(f"seed0: {seed_0}")
    return
    seed_1 = find_account(chain_maind_client.data_root, chain_id, "msigner1")["mnemonic"]
    wallet_0 = Wallet(seed_0)
    wallet_1 = Wallet(seed_1)
    to_address = "cro1hk220qwxp0c8m3pzazardmmfv8y0mg7ukdnn37"  # wallet_0.address

    #print multi wallet balance
    multi_wallet_addr = get_multi_addr(multi_wallet_name)
    balance = chain_maind_client.get_balance(multi_wallet_addr)
    print("multi address balance: ", balance)

    fee = StdFee.default()
    # account_num, sequence = 12, 0
    multi_wallet_addr = get_multi_addr(multi_wallet_name)
    account_num, sequence = chain_maind_client.get_account_info(multi_wallet_addr)
    print(f"account_num {account_num}, sequence: {sequence}")

    grpc_client = GrpcClient(chain_id, "0.0.0.0:26653", account_num, None)

    amount = "100"
    msg = MsgSend(from_address=multi_wallet_addr, to_address=to_address, amount=[Coin(amount)])

    # first make two single amino transaction, and create single_sig_v2
    sig_batch = list()
    threshold = 2

    pubkeys = [packed_to_any(ProtoPubKey(key=w.public_key)) for w in [wallet_0, wallet_1]]

    multi_pubkey = LegacyAminoPubKey(threshold=threshold, public_keys=pubkeys)
    for index, wallet in enumerate([wallet_0, wallet_1]):
        tx = Transaction(
            wallet=wallet,
            account_num=account_num,
            sequence=sequence,
            chain_id=chain_id,
            fee=fee,
            multi_sign_address=multi_wallet_addr
        )
        tx.add_msg(msg)
        single_sig_v2 = SingleSignatureV2(wallet.public_key, sequence, tx.signature)
        sig_batch.append(single_sig_v2)

    import pdb; pdb.set_trace()
    amount = [ProtoCoin(amount="10000", denom="basecro")]
    msg = grpc_client.get_packed_send_msg(multi_wallet_addr, to_address, amount)
    tx = gen_multi_tx(
        [msg],
        multi_pubkey,
        sig_batch,
        sequence,
    )
    response = grpc_client.broadcast_tx(tx)
    print(f"send tx response: {response}")


main()