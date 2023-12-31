
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


def send_tokens_with_payload(coin_object, coin_type):
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

    target_chain = 1
    target_recipient = "0x"+b58decode("4q2wPZMys1zCoAVpNmhgmofb6YM9MqLXmV25LdtEMAf9").hex()
    nonce = 0
    clock = "0x0000000000000000000000000000000000000000000000000000000000000006"
    wormhole_msg_fee = 0

    all_params = [
        hello_token_state,
        coin_object,
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
                    coin_type
                ]
            ]
        ]
    )


def redeem_tokens_with_payload(vaa: str, coin_type):
    # public entry fun external_redeem_transfer_with_payload<C>(
    #     t_state: &State,
    #     wormhole_state: &WormholeState,
    #     token_bridge_state: &mut TokenBridgeState,
    #     raw_vaa: vector<u8>,
    #     the_clock: &Clock,
    #     ctx: &mut TxContext
    # )

    hello_token_package_id = sui_project.network_config["hello_token"]
    token_bridge_state = sui_project.network_config["OBJECTS"]["TokenBridgeState"]
    hello_token_state = sui_project.network_config["OBJECTS"]["HelloTokenState"]
    wormhole_state = sui_project.network_config["OBJECTS"]["WormholeState"]

    hello_token = hello_token_package(hello_token_package_id)

    clock = "0x0000000000000000000000000000000000000000000000000000000000000006"
    raw_vaa = list(bytes.fromhex(vaa.replace("0x", "")))

    params = [
        hello_token_state,
        wormhole_state,
        token_bridge_state,
        raw_vaa,
        clock
    ]

    sui_project.batch_transaction(
        actual_params=params,
        transactions=[
            [
                hello_token.entry.external_redeem_transfer_with_payload,
                [
                    Argument("Input", U16(0)),
                    Argument("Input", U16(1)),
                    Argument("Input", U16(2)),
                    Argument("Input", U16(3)),
                    Argument("Input", U16(4)),
                ],
                [
                    coin_type
                ]
            ]
        ]
    )


if __name__ == '__main__':
    # coin10_type = "0xaf7326650ca2fd01227db4009ffe7cd805a60779712482be9462e9ef62cc4bbf::coin_10::COIN_10"
    wrapped_sol_type = "0xbc03aaab4c11eb84df8bf39fdc714fa5d5b65b16eb7d155e22c74a68c8d4e17f::coin::COIN"

    # vaa = "0x010000000001009a3cd8c977337270aca393614ca09caca46a50111b6f2374ac6966478816781b1201c0a9a4be484c76f72622610e1753eff897809225c3e1aa928e28ad6834010165169a990000000000013b26409f8aaded3f5ddca184695aa6a0fa829b0c85caf84856324896d214ca98000000000000638f20030000000000000000000000000000000000000000000000000000000000989680069b8857feab8184fb687f634618c035dac439dc1aeb3b5598a0f00000000001000135fbfedfe4ba06b311b86ae1d2064e08e583e6d550524307fc626648c4718c0c0015ceda17841d79db34bd17721d2024343b5d9dd0320626958e10f4cf3d800a719e01e76e8792889a2c3d6f7cf3b8b21be9c9f162ae98e1f218f23ac6d09e70931a2d"
    # redeem_tokens_with_payload(vaa, wrapped_sol_type)

    wrapped_sol_coin = "0x052f1e17c4e8b28e8754d464bc4e17c91cb28c102d9ebc0048ae85c6868e82c4"
    send_tokens_with_payload(wrapped_sol_coin, wrapped_sol_type)
