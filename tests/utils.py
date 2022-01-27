import platform
import shutil
import socket
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import requests
import yaml
from pystarport import cluster
from pystarport.ports import grpc_port, rpc_port

# constants in `configs/default.yaml`
ALICE = "alice"
BOB = "bob"

CRO_DENOM = "cro"
BASECRO_DENOM = "basecro"


def wait_for_block(cli, height, timeout=240):
    for _ in range(timeout * 2):
        try:
            status = cli.status()
        except AssertionError as e:
            print(f"get sync status failed: {e}", file=sys.stderr)
        else:
            current_height = int(status["SyncInfo"]["latest_block_height"])
            if current_height >= height:
                break
            print("current block height", current_height)
        time.sleep(0.5)
    else:
        raise TimeoutError(f"wait for block {height} timeout")


def wait_for_port(port, host="127.0.0.1", timeout=40.0):
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(0.1)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(
                    "Waited too long for the port {} on host {} to start accepting "
                    "connections.".format(port, host)
                ) from ex


_next_unique = 0


def gen_base_port():
    global _next_unique
    base_port = 10000 + _next_unique * 100
    _next_unique += 1
    return base_port


def cluster_fixture_aux(config_path, data_folder, cmd):
    base_port = gen_base_port()
    print("init cluster at", data_folder, ", base port:", base_port)
    cluster.init_cluster(data_folder, config_path, base_port, cmd=cmd)

    config = yaml.safe_load(open(config_path))
    clis = {}
    for key in config:
        chain_id = key
        clis[chain_id] = cluster.ClusterCLI(data_folder, chain_id=chain_id, cmd=cmd)

    supervisord = cluster.start_cluster(data_folder)

    try:
        for cli in clis.values():
            # wait for first node rpc port available before start testing
            wait_for_port(rpc_port(cli.config["validators"][0]["base_port"]))
            # wait for first node grpc port available before start testing
            wait_for_port(grpc_port(cli.config["validators"][0]["base_port"]))
            # wait for the first block generated before start testing
            wait_for_block(cli, 2)

        if len(clis) == 1:
            yield list(clis.values())[0]
        else:
            yield clis
    finally:
        supervisord.terminate()
        supervisord.wait()


def get_predefined_account_coins(blockchain_config_dict, account_name):
    account = [i for i in blockchain_config_dict["accounts"] if i["name"] == account_name]

    if len(account):
        return account[0]["coins"]
    else:
        raise ValueError(f"{account_name} not found in predefined accounts")


def get_blockchain_account_info(blockchain_accounts, account_name):
    account = [i for i in blockchain_accounts if i["name"] == account_name]

    if len(account):
        return account[0]
    else:
        raise ValueError(f"{account_name} not found in blockchain accounts")


def download_latest_binary(latest_release_info):
    latest_release_version = latest_release_info["tag_name"].lstrip("v")
    compatible_asset_name = (
        f"chain-main_{latest_release_version}_{platform.system()}_{platform.machine()}"
    )

    compatible_asset = [
        i for i in latest_release_info["assets"] if compatible_asset_name in i["name"]
    ]

    if len(compatible_asset):
        asset = compatible_asset[0]
        local_file = Path(__file__).parent.joinpath(asset["name"])
        extract_directory = Path(__file__).parent.joinpath(compatible_asset_name)

        data = requests.get(asset["browser_download_url"])
        with open(local_file, "wb") as f:
            f.write(data.content)

        tar = tarfile.open(local_file, "r:gz")
        tar.extractall(extract_directory)
        tar.close()

        shutil.copy2(
            Path(extract_directory).joinpath("bin", "chain-maind"),
            Path(__file__).parent.joinpath("chain-maind"),
        )

        shutil.rmtree(extract_directory)
        local_file.unlink()
    else:
        raise ValueError(
            f"{compatible_asset_name} could not be found on crypto-org-chain/chain-main GitHub release"  # noqa 501
        )


def check_local_chain_binary():
    chain_maind = Path(__file__).parent.joinpath("chain-maind")
    latest_release_info = requests.get(
        "https://api.github.com/repos/crypto-org-chain/chain-main/releases/latest"
    ).json()

    if chain_maind.is_file():
        process = subprocess.run([f"{chain_maind}", "version"], capture_output=True)

        latest_release_version = latest_release_info["tag_name"].lstrip("v")
        local_version = process.stdout.decode("utf-8").rstrip()

        if latest_release_version != local_version:
            print(
                f"download binary due to outdated version local: {local_version}, latest release: {latest_release_version}"  # noqa 501
            )
            download_latest_binary(latest_release_info)
    else:
        print("download binary due to missing chain-maind binary")
        download_latest_binary(latest_release_info)
