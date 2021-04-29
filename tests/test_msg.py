from chainlibpy.amino import (Coin, CommissionRates, Content, Description,
                              Input, Output, VoteOptionYes, message)


def test_msg():
    msg_send = message.MsgSend("from_address", "to_address", [Coin()])
    data = msg_send.to_dict()
    assert data == {
        "type": "cosmos-sdk/MsgSend",
        "value": {
            "from_address": "from_address",
            "to_address": "to_address",
            "amount": [{"amount": "0", "denom": "basecro"}],
        },
    }

    inputs = [Input("input_address", [Coin()])]
    outputs = [Output("output_address", [Coin()])]
    msg_multi_send = message.MsgMultiSend(inputs, outputs)
    data = msg_multi_send.to_dict()
    assert data == {
        "type": "cosmos-sdk/MsgMultiSend",
        "value": {
            "inputs": [
                {
                    "address": "input_address",
                    "coins": [{"amount": "0", "denom": "basecro"}],
                }
            ],
            "outputs": [
                {
                    "address": "output_address",
                    "coins": [{"amount": "0", "denom": "basecro"}],
                }
            ],
        },
    }

    msg = message.MsgVerifyInvariant(
        "sender_address", "invariant_module_name", "invariant_route"
    )
    data = msg.to_dict()
    assert data == {
        "type": "cosmos-sdk/MsgVerifyInvariant",
        "value": {
            "sender": "sender_address",
            "invariant_module_name": "invariant_module_name",
            "invariant_route": "invariant_route",
        },
    }

    msg = message.MsgSetWithdrawAddress("delegator_address", "withdraw_address")
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgSetWithdrawAddress",
        "value": {
            "delegator_address": "delegator_address",
            "withdraw_address": "withdraw_address",
        },
    }

    msg = message.MsgWithdrawDelegationReward("delegator_address", "validator_address")
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgWithdrawDelegationReward",
        "value": {
            "delegator_address": "delegator_address",
            "validator_address": "validator_address",
        },
    }

    msg = message.MsgWithdrawValidatorCommission("validator_address")
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgWithdrawValidatorCommission",
        "value": {"validator_address": "validator_address"},
    }

    msg = message.MsgFundCommunityPool([Coin()], "depositor")
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgFundCommunityPool",
        "value": {
            "amount": [{"amount": "0", "denom": "basecro"}],
            "depositor": "depositor",
        },
    }

    evidence_content = Content("type_url", b"evidence content details")
    msg = message.MsgSubmitEvidence("submitter", evidence_content)
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgSubmitEvidence",
        "value": {
            "submitter": "submitter",
            "evidence": {"type_url": "type_url", "value": b"evidence content details"},
        },
    }

    content = Content("type_url", b"content details")
    msg = message.MsgSubmitProposal(content, [Coin()], "proposer")
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgSubmitProposal",
        "value": {
            "content": {"type_url": "type_url", "value": b"content details"},
            "initial_deposit": [{"amount": "0", "denom": "basecro"}],
            "proposer": "proposer",
        },
    }

    msg = message.MsgVote(1, "voter address", VoteOptionYes)
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgVote",
        "value": {"proposal_id": 1, "voter": "voter address", "option": VoteOptionYes},
    }

    msg = message.MsgDeposit(1, "depositor address", [Coin()])
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgDeposit",
        "value": {
            "proposal_id": 1,
            "depositor": "depositor address",
            "amount": [{"amount": "0", "denom": "basecro"}],
        },
    }

    msg = message.MsgUnjail("validator address")
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgUnjail",
        "value": {"validator_addr": "validator address"},
    }

    description = Description(
        "moniker", "identity", "website", "security_contact", "details"
    )
    commission = CommissionRates("rate", "max_rate", "max_change_rate")
    msg = message.MsgCreateValidator(
        description,
        commission,
        "min_self_delegation",
        "delegator_address",
        "validator_address",
        "public key",
        Coin(),
    )
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgCreateValidator",
        "value": {
            "description": {
                "moniker": "moniker",
                "identity": "identity",
                "website": "website",
                "security_contact": "security_contact",
                "details": "details",
            },
            "commission": {
                "rate": "rate",
                "max_rate": "max_rate",
                "max_change_rate": "max_change_rate",
            },
            "min_self_delegation": "min_self_delegation",
            "delegator_address": "delegator_address",
            "validator_address": "validator_address",
            "pubkey": "public key",
            "value": {"amount": "0", "denom": "basecro"},
        },
    }

    msg = message.MsgEditValidator(
        description, "validator_address", commission, "min_self_delegation"
    )
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgEditValidator",
        "value": {
            "description": {
                "moniker": "moniker",
                "identity": "identity",
                "website": "website",
                "security_contact": "security_contact",
                "details": "details",
            },
            "validator_address": "validator_address",
            "commission_rate": {
                "rate": "rate",
                "max_rate": "max_rate",
                "max_change_rate": "max_change_rate",
            },
            "min_self_delegation": "min_self_delegation",
        },
    }

    msg = message.MsgDelegate("delegator_address", "validator_address", Coin())
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgDelegate",
        "value": {
            "delegator_address": "delegator_address",
            "validator_address": "validator_address",
            "amount": {"amount": "0", "denom": "basecro"},
        },
    }

    msg = message.MsgBeginRedelegate(
        "delegator_address", "validator_src_address", "validator_dst_address", Coin()
    )
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgBeginRedelegate",
        "value": {
            "delegator_address": "delegator_address",
            "validator_src_address": "validator_src_address",
            "validator_dst_address": "validator_dst_address",
            "amount": {"amount": "0", "denom": "basecro"},
        },
    }

    msg = message.MsgUndelegate("delegator_address", "validator_address", Coin())
    data = msg.to_dict()
    print(data)
    assert data == {
        "type": "cosmos-sdk/MsgUndelegate",
        "value": {
            "delegator_address": "delegator_address",
            "validator_address": "validator_address",
            "amount": {"amount": "0", "denom": "basecro"},
        },
    }
