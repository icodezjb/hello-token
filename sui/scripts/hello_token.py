
from base58 import b58decode
from load import hello_token_package, sui_project, wormhole_package, token_bridge_package
from sui_brownie import Argument, U16

sui_project.active_account("TestAccount")

def create_state():
    # public fun create_state(
    #     owner_cap: &mut OwnerCap,
    #     upgrade_cap: UpgradeCap,
    #     wormhole_state: &WormholeState,
    #     relayer_fee: u64,
    #     relayer_fee_precision: u64,
    #     ctx: &mut TxContext
    # )

    hello_token_package_id = sui_project.network_config["hello_token"]
    wormhole_state = sui_project.network_config["OBJECTS"]["WormholeState"]
    owner_cap = sui_project.network_config["OBJECTS"]["OwnerCap"]
    upgrade_cap = sui_project.network_config["OBJECTS"]["UpgradeCap"]

    relayer_fee = 10
    relayer_fee_precision = 100000

    hello_token = hello_token_package(hello_token_package_id)

    params = [
        owner_cap,
        upgrade_cap,
        wormhole_state,
        relayer_fee,
        relayer_fee_precision
    ]

    sui_project.batch_transaction(
        actual_params=params,
        transactions=[
            [
                hello_token.owner.create_state,
                [
                    Argument("Input", U16(0)),
                    Argument("Input", U16(1)),
                    Argument("Input", U16(2)),
                    Argument("Input", U16(3)),
                    Argument("Input", U16(4))
                ],
                []
            ]
        ]
    )


def register_foreign_contract():
    # public fun register_foreign_contract(
    #     _: &OwnerCap,
    #     t_state: &mut State,
    #     chain: u16,
    #     contract_address: address,
    # )

    hello_token_package_id = sui_project.network_config["hello_token"]
    solana_program = sui_project.network_config["solana_program"]
    hello_token_state = sui_project.network_config["OBJECTS"]["HelloTokenState"]
    owner_cap = sui_project.network_config["OBJECTS"]["OwnerCap"]
    solana_chain_id = 1


    hello_token = hello_token_package(hello_token_package_id)

    params = [
        owner_cap,
        hello_token_state,
        solana_chain_id,
        "0x"+b58decode(solana_program).hex()
    ]

    sui_project.batch_transaction(
        actual_params=params,
        transactions=[
            [
                hello_token.owner.register_foreign_contract,
                [
                    Argument("Input", U16(0)),
                    Argument("Input", U16(1)),
                    Argument("Input", U16(2)),
                    Argument("Input", U16(3))
                ],
                []
            ]
        ]
    )


def send_tokens_with_payload():
    # public entry fun external_send_tokens_with_payload<C>(
    #     t_state: &State,
    #     coins: Coin<C>,
    #     token_bridge_state: &mut TokenBridgeState,
    #     target_chain: u16,
    #     target_recipient: address,
    #     nonce: u32,
    #     wormhole_state: &mut WormholeState,
    #     message_fee: Coin<SUI>,
    #     the_clock: &Clock,
    #     ctx: & TxContext
    # )

    hello_token_package_id = sui_project.network_config["hello_token"]
    token_bridge_state = sui_project.network_config["OBJECTS"]["TokenBridgeState"]
    hello_token_state = sui_project.network_config["OBJECTS"]["HelloTokenState"]
    wormhole_state = sui_project.network_config["OBJECTS"]["WormholeState"]

    hello_token = hello_token_package(hello_token_package_id)

    coin10_type = "0xaf7326650ca2fd01227db4009ffe7cd805a60779712482be9462e9ef62cc4bbf::coin_10::COIN_10"
    target_chain = 1
    target_recipient = "0x"+b58decode("4q2wPZMys1zCoAVpNmhgmofb6YM9MqLXmV25LdtEMAf9").hex()
    nonce = 0
    clock = "0x0000000000000000000000000000000000000000000000000000000000000006"
    transfer_coin10 = "0xd7b0aceb50df6ee5c88ef850f5e9f94fca533f5af99214b818f32f32f926bf17"
    wormhole_msg_fee = 0

    all_params = [
        hello_token_state,
        transfer_coin10,
        token_bridge_state,
        target_chain,
        target_recipient,
        nonce,
        wormhole_state,
        wormhole_msg_fee,
        clock
    ]

    sui_project.batch_transaction(
        actual_params=all_params,
        transactions=[
            [
                hello_token.entry.external_send_tokens_with_payload,
                [
                    Argument("Input", U16(0)),
                    Argument("Input", U16(1)),
                    Argument("Input", U16(2)),
                    Argument("Input", U16(3)),
                    Argument("Input", U16(4)),
                    Argument("Input", U16(5)),
                    Argument("Input", U16(6)),
                    Argument("Input", U16(7)),
                    Argument("Input", U16(8)),
                ],
                [
                    coin10_type
                ]
            ]
        ]
    )



if __name__ == '__main__':
    # create_state()
    # register_foreign_contract()
    send_tokens_with_payload()
