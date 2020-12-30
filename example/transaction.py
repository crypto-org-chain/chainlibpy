#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

import requests

from chainlibpy import Transaction, Wallet


def main():
    seed = "dune car envelope chuckle elbow slight proud fury remove candy uphold puzzle call select sibling sport gadget please want vault glance verb damage gown"
    wallet_1 = Wallet(seed)
    address_1 = wallet_1.address
    print(address_1)
    wallet_2 = Wallet.new()
    address_2 = wallet_2.address
    print(address_2)

    # the api port setted in ${home_dir of chain-maind}/config/app.toml, the default is ~/.chain-maind/config/app.toml
    base_url = "http://127.0.0.1:1317"
    url_tx = f"{base_url}/txs"
    url_account = f"{base_url}/cosmos/auth/v1beta1/accounts/{address_1}"
    url_balance = f"{base_url}/cosmos/bank/v1beta1/balances/{address_1}"

    # get the balance of address_1
    response = requests.get(url_balance)
    balance_1 = int(response.json()["balances"][0]["amount"])
    print(f"balance of address 1: {balance_1}")

    # get the account info
    response = requests.get(url_account)
    account_info = response.json()["account"]
    account_num = int(account_info["account_number"])
    sequence = int(account_info["sequence"])

    # make transaction
    tx = Transaction(
        wallet=wallet_1,
        account_num=account_num,
        sequence=sequence,
        chain_id="test",
        fee=100000,
        gas=300000,
    )
    amount = 1 * 10 ** 8
    tx.add_transfer(to_address=address_2, amount=amount)
    signed_tx = tx.get_pushable()
    print("signed tx:", signed_tx)
    response = requests.post(url_tx, json=signed_tx)
    if not response.ok:
        raise Exception(response.reason)
    result = response.json()
    print(result)
    if result.get("code"):
        raise Exception(result["raw_log"])

    # get the balance after sync
    time.sleep(5)
    response = requests.get(url_balance)
    balance_1_after = int(response.json()["balances"][0]["amount"])
    print(f"balance of address 1 after transfer: {balance_1_after}")


if __name__ == "__main__":
    main()
