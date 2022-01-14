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
  - [Using secure gRPC channel](#using-secure-grpc-channel)
- [Acknowledgement](#acknowledgement)
- [Development](#development)
  - [Set up development environment](#set-up-development-environment)
  - [Generate gRPC code](#generate-grpc-code)
  - [Tox](#tox)

<!-- mdformat-toc end -->

## Installing<a name="installing"></a>

Require Python >= 3.7, installing from PyPI repository (https://pypi.org/project/chainlibpy):

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

```python
from chainlibpy.generated.cosmos.base.v1beta1.coin_pb2 import Coin
from chainlibpy.grpc_client import GrpcClient
from chainlibpy.transaction import sign_transaction
from chainlibpy.wallet import Wallet

# Refer to example/transaction.py for how to obtain CONSTANT values below
DENOM = "basecro"
MNEMONIC_PHRASE = "first ... last"
TO_ADDRESS = "cro...add"
AMOUNT = [Coin(amount="10000", denom=DENOM)]
CHAIN_ID = "chainmaind"
GRPC_ENDPOINT = "0.0.0.0:26653"

wallet = Wallet(MNEMONIC_PHRASE)
client = GrpcClient(wallet, CHAIN_ID, GRPC_ENDPOINT)

from_address = wallet.address
account_number = client.query_account_data(wallet.address).account_number

msg = client.get_packed_send_msg(wallet.address, TO_ADDRESS, AMOUNT)
tx = client.generate_tx([msg], [wallet.address], [wallet.public_key])
sign_transaction(tx, wallet.private_key, CHAIN_ID, account_number)
client.broadcast_tx(tx)
```

You may also refer to `example/transaction.py` on how to use a high level function `bank_send()` to sign and broadcast a transaction

### Using secure gRPC channel<a name="using-secure-grpc-channel"></a>

Please refer to `example/secure_channel_example.py` on how to use secure gRPC channel with server certificate

## Acknowledgement<a name="acknowledgement"></a>

Thanks [cosmospy](https://github.com/hukkinj1/cosmospy) for the following:

- referenced the packages to sign transaction and create hd wallet
- python lint config file
- use same sign method

## Development<a name="development"></a>

### Set up development environment<a name="set-up-development-environment"></a>

More about [poetry](https://python-poetry.org/docs/).

```
poetry install
```

### Generate gRPC code<a name="generate-grpc-code"></a>

```
poetry shell
./generated_protos.sh
```

**NOTE:** By default, `master` branch of `cosmos-sdk` is used. Use command below to download a different version:

```
./generated_protos.sh -COSMOS_REF=v0.44.5
```

If more generated gRPC code is needed in the future, please add the `.proto` files needed here in `generated_protos.sh`:

```bash
# Add .proto files here to generate respective gRPC code
PROTO_FILES="
$COSMOS_SDK_DIR/proto/cosmos/auth/v1beta1/auth.proto
...
```

### Tox<a name="tox"></a>

```
pyenv local 3.8.a 3.9.b
```

`a` and `b` are python versions installed on your computer by `pyenv`. More about [pyenv](https://github.com/pyenv/pyenv).

After this command, a `.python-version` file will be generated at project root directory, which means python versions inside `.python-version` are presented for this project. So running `tox` command with `py{38,39}` configuration should succeed.\
Then run to verify. Command below is recommended to run before pushing a commit.

```sh
poetry run tox
# or
poetry shell
tox
```
