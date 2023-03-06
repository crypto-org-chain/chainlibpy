# 🚨 DEPRECATED 🚨 

This repo has been deprecated. You can generate protobuf code yourself or generate Python bindings directly from [DeFi Wallet Core](https://github.com/crypto-com/defi-wallet-core-rs#python) instead. Please reference that repository in the future.

-------

[![Build Status](https://travis-ci.com/crypto-org-chain/chainlibpy.svg?branch=master)](https://travis-ci.com//chainlibpy)
[![codecov.io](https://codecov.io/gh/crypto-org-chain/chainlibpy/branch/master/graph/badge.svg)](https://codecov.io/gh/crypto-org-chain/chainlibpy)
[![PyPI version](https://img.shields.io/pypi/v/chainlibpy)](https://pypi.org/project/chainlibpy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# chainlibpy

> Tools for [Crypto.org Chain](https://github.com/crypto-org-chain/chain-main) wallet management and offline transaction signing

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=2 -->

- [Installing](#installing)
- [Usage](#usage)
  - [Generating a wallet](#generating-a-wallet)
  - [Signing and broadcasting a transaction](#signing-and-broadcasting-a-transaction)
  - [Interact with mainnet or testnet](#interact-with-mainnet-or-testnet)
- [Acknowledgement](#acknowledgement)
- [Development](#development)
  - [Set up development environment](#set-up-development-environment)
  - [Add pre-commit git hook](#add-pre-commit-git-hook)
  - [Generate gRPC code](#generate-grpc-code)
  - [Tox](#tox)

<!-- mdformat-toc end -->

## Installing<a name="installing"></a>

Require Python >= 3.8, installing from [PyPI repository](https://pypi.org/project/chainlibpy):

```bash
pip install chainlibpy
```

## Usage<a name="usage"></a>

### Generating a wallet<a name="generating-a-wallet"></a>

```python
from chainlibpy import Wallet

# create a wallet
wallet = Wallet.new()
# or you can recover from an mnomic
# mnemonic = "dune car envelope chuckle elbow slight proud fury remove candy uphold puzzle call select sibling sport gadget please want vault glance verb damage gown"
# wallet = Wallet(mnemonic)

print(wallet.private_key)
print(wallet.public_key)
print(wallet.address)
```

### Signing and broadcasting a transaction<a name="signing-and-broadcasting-a-transaction"></a>

Please refer to `example/transaction.py` for how to start a local testnet with `pystarport` and change information below to run the examples successfully.

```diff
# Obtained from {directory_started_pystarport}/data/chainmaind/accounts.json
# To recover one of the genesis account
- MNEMONIC_PHRASE = "first ... last"
+ MNEMONIC_PHRASE = "REMEMBER TO CHANGE"
# Obtained from {directory_started_pystarport}/data/chainmaind/accounts.json
- TO_ADDRESS = "cro...add"
+ TO_ADDRESS = "REMEMBER TO CHANGE"
```

### Interact with mainnet or testnet<a name="interact-with-mainnet-or-testnet"></a>

Please refer to `example/secure_channel_example.py` on how to use secure gRPC channel with server certificate to interact with mainnet or testnet.

## Acknowledgement<a name="acknowledgement"></a>

Thanks to [cosmospy](https://github.com/hukkinj1/cosmospy) for the following:

- referenced the packages to sign transaction and create hd wallet
- python lint config file
- use same sign method

Thanks to [eth-utils](https://github.com/ethereum/eth-utils) for the following:

- Conversion of different units without facing precision issues in Python

## Development<a name="development"></a>

### Set up development environment<a name="set-up-development-environment"></a>

Run command below to install dependencies (more about [poetry](https://python-poetry.org/docs/)):

```bash
poetry install
```

### Add pre-commit git hook<a name="add-pre-commit-git-hook"></a>

To set up the git hook scripts, so that [`pre-commit`](https://pre-commit.com/) will run automatically on `git commit`:

```bash
pre-commit install
```

### Generate gRPC code<a name="generate-grpc-code"></a>

```bash
poetry shell
./generated_protos.sh
```

**NOTE:** By default, `master` branch of `cosmos-sdk` is used. Use command below to download a different version:

```bash
./generated_protos.sh -COSMOS_REF=v0.44.5
```

If more generated gRPC code is needed in the future, please add the path to `.proto` file needed here in `generated_protos.sh`:

```diff
# Add .proto files here to generate respective gRPC code
PROTO_FILES="
$COSMOS_SDK_DIR/proto/cosmos/auth/v1beta1/auth.proto
+$COSMOS_SDK_DIR/proto/other.proto
...
```

### Tox<a name="tox"></a>

[Tox](https://tox.wiki/en/latest/) is a tool to automate and standardize testing processes in Python.

For this project, the list of environment that will be run when invoking `tox` command is `py{38,39}`. Hence we need to set up Python 3.8 and 3.9 for this project. Run command below to set a local application-specific Python version (in this case 3.8 and 3.9) with [pyenv](https://github.com/pyenv/pyenv):

```bash
pyenv local 3.8.a 3.9.b
```

**Note:** `a` and `b` are python versions installed on your computer by `pyenv`.

After running command above, a `.python-version` file will be generated, which means python versions inside `.python-version` are presented for this project. Now, running command `tox` should succeed without prompting environment missing error.

Run command below to verify:

```bash
poetry run tox
# or
poetry shell
tox
```

It is also recommended to run `tox` command before pushing a commit.
