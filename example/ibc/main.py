import json
import subprocess
import time
from pathlib import Path

import requests
import yaml
from pystarport.cluster import (ClusterCLI, find_account, init_cluster,
                                interact, start_cluster)
from pystarport.ports import api_port

from chainlibpy import Transaction, Wallet
from chainlibpy.amino import Coin, StdFee, TimeoutHeight
from chainlibpy.amino.message import IbcMsgTransfer


class Runner():
    '''
    we use pystarport to create the IBC env
    need to install hermes: https://github.com/informalsystems/ibc-rs/releases
    '''
    def __init__(self, data_root=Path("/tmp/data"), config_file="config.yaml"):
        self.data_root = data_root
        self.config_file = config_file

    @property
    def cluster(self):
        config = yaml.safe_load(open(self.config_file))
        clis = {}
        for key in config:
            if key == "relayer":
                continue
            chain_id = key
            clis[chain_id] = ClusterCLI(self.data_root, chain_id=chain_id)
        return clis

    def url_base(self, chain_id, index=0):
        cli = self.cluster[chain_id]
        port = cli.base_port(index)
        return "http://127.0.0.1:{}".format(api_port(port))

    def get_balance(self, chain_id, index, address):
        url_base = self.url_base(chain_id, index)
        url_balance = f"{url_base}/cosmos/bank/v1beta1/balances/{address}"
        response = requests.get(url_balance)
        balance = int(response.json()["balances"][0]["amount"])
        return balance

    def get_account_info(self, chain_id, index, address):
        url_base = self.url_base(chain_id, index)
        url_account = f"{url_base}/cosmos/auth/v1beta1/accounts/{address}"
        response = requests.get(url_account)
        account_info = response.json()["account"]
        account_num = int(account_info["account_number"])
        sequence = int(account_info["sequence"])
        return account_num, sequence

    def send_tx(self, chain_id, index, data):
        url_base = self.url_base(chain_id, index)
        url = f"{url_base}/txs"
        response = requests.post(url, json=data)
        return response

    def init_relayer(self):
        relayer = ["hermes", "-j", "-c", self.data_root / "relayer.toml"]
        subprocess.run(
            relayer
            + [
                "create",
                "channel",
                "ibc-0",
                "ibc-1",
                "--port-a",
                "transfer",
                "--port-b",
                "transfer",
            ],
            check=True,
            )

        # start relaying
        self.cluster["ibc-0"].supervisor.startProcess("relayer-demo")

    @property
    def relayer_channels(self):
        # all clusters share the same root data directory
        relayer = ["hermes", "-j", "-c", self.data_root / "relayer.toml"]
        rsp = json.loads(subprocess.check_output(relayer + ["query", "channels", "ibc-0"]))
        src_channel = rsp["result"][0]["channel_id"]
        rsp = json.loads(subprocess.check_output(relayer + ["query", "channels", "ibc-1"]))
        dst_channel = rsp["result"][0]["channel_id"]
        return src_channel, dst_channel

    def start(self):
        '''
        after start the tasks, you can use `supervisorctl -c task.ini` to see the status of each program
        '''
        data_path = "/tmp/dadta"
        interact(f"rm -r {data_path}; mkdir -p {data_path}", ignore_error=True)
        data_dir = Path("/tmp/data")
        init_cluster(data_dir, "config.yaml", 26650)
        start_cluster(data_dir)
        time.sleep(10)
        self.init_relayer()

def test_ibc():
    r = Runner()
    # r.start()
    # time.sleep(10)
    seed_0 = find_account(r.data_root, "ibc-0", "relayer")["mnemonic"]
    seed_1 = find_account(r.data_root, "ibc-1", "relayer")["mnemonic"]
    wallet_0 = Wallet(seed_0)
    wallet_1 = Wallet(seed_1)
    addr_0 = wallet_0.address
    addr_1 = wallet_1.address
    src_channel, dst_channel = r.relayer_channels

    # do a transfer from ibc-0 to ibc-1
    print("transfer ibc0 -> ibc1")
    account_num, sequence = r.get_account_info("ibc-0", 0, addr_0)
    fee = StdFee("300000", [Coin("100000")])
    tx = Transaction(
        wallet=wallet_0,
        account_num=account_num,
        sequence=sequence,
        chain_id="ibc-0",
        fee=fee,
    )
    amount = Coin("10000")
    target_version = 1
    timeout_height = TimeoutHeight(str(target_version), "10000000000")
    msg = IbcMsgTransfer(
        source_port="transfer",
        source_channel=src_channel,
        sender=addr_0,
        receiver=addr_1,
        coin=amount,
        packet_timeout_height=timeout_height,
        packet_timeout_timestamp="0",
        absolute_timeouts=True,
    )
    tx.add_msg(msg)
    signed_tx = tx.get_pushable()
    response = r.send_tx("ibc-0", 0, signed_tx)
    if not response.ok:
        raise Exception(response.reason)
    else:
        result = response.json()
        print("send tx result:", result)
        if result.get("code"):
            raise Exception(result["raw_log"])
    # get the balance after sync
    time.sleep(5)
    # get the ibc-0 balance
    balance_0 = r.get_balance("ibc-0", 0, addr_0)
    print("balance 0 after transfer: ", balance_0)

    balance_1 = r.get_balance("ibc-1", 0, addr_1)
    print("balance 1 after transfer: ", balance_1)

    # do a transfer from ibc-1 to ibc-0
    print("transfer ibc1 -> ibc0")
    account_num, sequence = r.get_account_info("ibc-1", 0, addr_1)
    tx = Transaction(
        wallet=wallet_1,
        account_num=account_num,
        sequence=sequence,
        chain_id="ibc-1",
    )
    amount = Coin("10000", f"transfer/{dst_channel}/basecro")
    target_version = 0
    timeout_height = TimeoutHeight(str(target_version), "10000000000")
    msg = IbcMsgTransfer(
        source_port="transfer",
        source_channel=dst_channel,
        sender=addr_1,
        receiver=addr_0,
        coin=amount,
        packet_timeout_height=timeout_height,
        packet_timeout_timestamp="0",
        absolute_timeouts=True,
    )
    tx.add_msg(msg)
    signed_tx = tx.get_pushable()
    response = r.send_tx("ibc-1", 0, signed_tx)
    if not response.ok:
        raise Exception(response.reason)
    else:
        result = response.json()
        print("send tx result:", result)
        if result.get("code"):
            raise Exception(result["raw_log"])
    # get the balance after sync
    time.sleep(50)
    # get the ibc-0 balance
    balance_0 = r.get_balance("ibc-0", 0, addr_0)
    print("balance 0 after transfer: ", balance_0)
    balance_1 = r.get_balance("ibc-1", 0, addr_1)
    print("balance 1 after transfer: ", balance_1)

if __name__ == "__main__":
    test_ibc()
