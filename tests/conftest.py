import json
from pathlib import Path

import pytest
import toml
import yaml

from chainlibpy import NetworkConfig

from .utils import check_local_chain_binary, cluster_fixture_aux


@pytest.fixture(scope="session")
def config_path() -> Path:
    return Path(__file__).parent.joinpath("configs", "default.yaml")


@pytest.fixture(scope="session")
def data_folder(tmp_path_factory: "pytest.TempPathFactory") -> "Path":
    return tmp_path_factory.mktemp("data")


@pytest.fixture(scope="session", autouse=True)
def cluster(data_folder, config_path):
    check_local_chain_binary()

    cmd = Path(__file__).parent.joinpath("chain-maind")
    yield from cluster_fixture_aux(config_path, data_folder, cmd)


@pytest.fixture(scope="session")
def chain_id(config_path):
    with open(config_path, "r") as f:
        chain_config = yaml.safe_load(f)

    # Assumption: only one chain should be spawned by pystarport from config file
    if len(chain_config) == 1:
        return list(chain_config.keys())[0]
    else:
        raise TypeError("Not exactly one chain found in config file")


@pytest.fixture(scope="session")
def blockchain_config_dict(config_path, chain_id):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config[chain_id]


@pytest.fixture(scope="session")
def blockchain_accounts(data_folder: "Path", chain_id):
    with open(data_folder.joinpath(chain_id, "accounts.json"), "r") as f:
        account_dict = json.load(f)
    return account_dict


@pytest.fixture(scope="session", autouse=True)
def local_test_network_config(data_folder: "Path", chain_id):
    validator0_app_config_file = data_folder.joinpath(chain_id, "node0", "config", "app.toml")
    validator0_tm_config_file = data_folder.joinpath(chain_id, "node0", "config", "config.toml")

    if not Path(validator0_app_config_file).is_file():
        raise FileNotFoundError(f"{validator0_app_config_file} not found")

    if not Path(validator0_tm_config_file).is_file():
        raise FileNotFoundError(f"{validator0_tm_config_file} not found")

    with open(validator0_app_config_file, "r") as f:
        validator0_app_config = toml.load(f)

    with open(validator0_tm_config_file, "r") as f:
        validator0_tm_config = toml.load(f)

    return NetworkConfig(
        grpc_endpoint=validator0_app_config["grpc"]["address"].replace(
            "tcp://0.0.0.0", "http://127.0.0.1"
        ),
        tendermint_rpc=validator0_tm_config["rpc"]["laddr"].replace(
            "tcp://0.0.0.0", "http://127.0.0.1"
        ),
        rest_api=validator0_app_config["api"]["address"].replace(
            "tcp://0.0.0.0", "http://127.0.0.1"
        ),
        chain_id=chain_id,
        address_prefix="cro",
        coin_denom="cro",
        coin_base_denom="basecro",
        exponent=8,
        derivation_path="m/44'/394'/0'/0/0",
    )
