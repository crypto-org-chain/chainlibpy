[![Build Status](https://travis-ci.com/crypto-com/chainlibpy.svg?branch=master)](https://travis-ci.com//chainlibpy)
[![codecov.io](https://codecov.io/gh/crypto-com/chainlibpy/branch/master/graph/badge.svg)](https://codecov.io/gh/crypto-com/chainlibpy)
[![PyPI version](https://img.shields.io/pypi/v/chainlibpy)](https://pypi.org/project/chainlibpy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# chainlibpy

<!--- Don't edit the version line below manually. Let bump2version do it for you. -->

> Version 1.0.0

> Tools for [Crypto.com](https://github.com/crypto-com/chain-main) wallet management and offline transaction signing

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=2 -->

- [Installing](<#installing>)
- [Usage](<#usage>)
  - [Generating a wallet](<#generating-a-wallet>)
  - [Signing transactions](<#signing-transactions>)
  - [thanks](<#thanks>)

<!-- mdformat-toc end -->

## Installing<a name="installing"></a>

Installing from PyPI repository (https://pypi.org/project/chainlibpy):

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

### Signing transactions<a name="signing-transactions"></a>

```python
from chainlibpy import Transaction, Wallet

wallet = Wallet.new()
tx = Transaction(
    wallet=wallet,
    account_num=11335,
    sequence=0,
    fee=1000,
    gas=70000,
    memo="",
    chain_id="test",
    sync_mode="sync",
)
tx.add_transfer(to_address="cro103l758ps7403sd9c0y8j6hrfw4xyl70j4mmwkf", amount=387000)
pushable_tx = tx.get_pushable()
```

One or more token transfers can be added to a transaction by calling the `add_transfer` method.

When the transaction is fully prepared, calling `get_pushable` will return a signed transaction in the form of a JSON string.
This can be used as request body when calling the `POST /txs` endpoint of rpc.

### thanks<a name="thanks"></a>

thanks [cosmospy](https://github.com/hukkinj1/cosmospy) for the following:

- referenced the packages to sign transaction and create hd wallet
- python lint config file
- use same sign method
