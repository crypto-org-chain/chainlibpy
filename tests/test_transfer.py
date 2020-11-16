from cryptopy import Transaction, Wallet


def main():
    # hd1 = generate_wallet()
    # print(hd1)
    # hd2 = generate_wallet()
    # print(hd2)
    # seed2 = "noble chalk joke night habit night teach whip festival lawn twice warfare net south elbow oppose uphold quiz airport pledge aim soul scorpion obscure"
    seed = "dune car envelope chuckle elbow slight proud fury remove candy uphold puzzle call select sibling sport gadget please want vault glance verb damage gown"
    wallet = Wallet(seed)

    amount = 1000000000
    denom = "basecro"
    chain_id = "test"
    tx = Transaction(
        wallet=wallet,
        account_num=0,
        sequence=0,
        chain_id=chain_id,
        timeout_height=1,
    )
    tx.add_transfer(
        to_address="cro1sza72v70tm9l38h6uxhwgra5eg33xd4jr3ujl7", amount=amount, denom=denom
    )
    pushable_tx = tx.get_pushable()
    print(pushable_tx)


main()
