import json
from pathlib import Path

import requests
import yaml
from pystarport.cluster import (ClusterCLI, find_account, init_cluster,
                                interact, start_cluster)
from pystarport.ports import api_port

from chainlibpy import Transaction, Wallet
from chainlibpy.amino.message import MsgIssueDenom


class Runner():
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

    def send_tx(self, chain_id, index, data):
        url_base = self.url_base(chain_id, index)
        url = f"{url_base}/txs"
        response = requests.post(url, json=data)
        return response

    def get_account_info(self, chain_id, index, address):
        url_base = self.url_base(chain_id, index)
        url_account = f"{url_base}/cosmos/auth/v1beta1/accounts/{address}"
        response = requests.get(url_account)
        account_info = response.json()["account"]
        account_num = int(account_info["account_number"])
        sequence = int(account_info["sequence"])
        return account_num, sequence

    def start(self):
        '''
        after start the tasks, you can use `supervisorctl -c task.ini` to see the status of each program
        '''
        data_path = "/tmp/data"
        interact(f"rm -r {data_path}; mkdir -p {data_path}", ignore_error=True)
        data_dir = Path("/tmp/data")
        init_cluster(data_dir, "config.yaml", 26650)
        start_cluster(data_dir)



def test_create_nft():
    r = Runner()
    chain_id = "chain_id_test"
    seed_0 = find_account(r.data_root, chain_id, "signer1")["mnemonic"]
    wallet_0 = Wallet(seed_0)
    account_num, sequence = r.get_account_info(chain_id, 0, wallet_0.address)
    tx = Transaction(
        wallet=wallet_0,
        account_num=account_num,
        sequence=sequence,
        chain_id=chain_id,
    )
    schema={
               "title":"Asset Metadata",
               "type":"object",
               "properties": {"name": {"type":"string", "description":"testidentity"},
                              "description": {"type":"string","description":"testdescription"},
                               "image": {"type":"string","description":"testdescription"}
                              }
           },
    msg = MsgIssueDenom(
         sender=wallet_0.address,
         id="testdenomid",
         name="testdenomname",
         schema=schema,
    )
    tx.add_msg(msg)
    signed_tx = tx.get_pushable()
    response = r.send_tx(chain_id, 0, signed_tx)
    if not response.ok:
        raise Exception(response.reason)
    else:
        result = response.json()
        print("send tx result:", result)
        if result.get("code"):
            raise Exception(result["raw_log"])

def test():
    r = Runner()
    chain_id = "chain_id_test"
    seed_0 = find_account(r.data_root, chain_id, "signer1")["mnemonic"]
    wallet_0 = Wallet(seed_0)
    cluster = r.cluster[chain_id]
    denomid = "testdenomid2"
    denomname = "testdenomname2"
    response = cluster.create_nft(wallet_0.address, denomid, denomname)
    raw_log = json.loads(response["raw_log"])
    print(raw_log)

if __name__ == "__main__":
    # r = Runner()
    # r.start()
    # time.sleep(10)
    test_create_nft()
