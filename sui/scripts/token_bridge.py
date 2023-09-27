import base64

import requests
from load import token_bridge_package, wormhole_package, sui_project
from sui_brownie import Argument, U16

sui_project.active_account("TestAccount")

def attest_token():
    # public fun attest_token<CoinType>(
    #     token_bridge_state: &mut State,
    #     coin_meta: &CoinMetadata<CoinType>,
    #     nonce: u32
    # ): MessageTicket

    token_bridge_package_id = sui_project.network_config["token_bridge"]
    wormhole_package_id = sui_project.network_config["wormhole"]
    token_bridge_state = sui_project.network_config["OBJECTS"]["TokenBridgeState"]
    wormhole_state = sui_project.network_config["OBJECTS"]["WormholeState"]
    coin_meta_10 = sui_project.network_config["OBJECTS"]["CoinMetadata10"]
    coin10_type = "0xaf7326650ca2fd01227db4009ffe7cd805a60779712482be9462e9ef62cc4bbf::coin_10::COIN_10"

    wormhole_messge_fee = 0
    clock = "0x0000000000000000000000000000000000000000000000000000000000000006"

    token_bridge = token_bridge_package(token_bridge_package_id)
    wormhole = wormhole_package(wormhole_package_id)

    params = [
        wormhole_state,
        token_bridge_state, # 1
        coin_meta_10,
        0 , # nonce,
        wormhole_messge_fee,
        clock
    ]

    sui_project.batch_transaction(
        actual_params=params,
        transactions=[
            [
                token_bridge.attest_token.attest_token,
                [
                    Argument("Input", U16(1)),
                    Argument("Input", U16(2)),
                    Argument("Input", U16(3)),
                ],
                [
                    coin10_type
                ]
            ],
            [
                wormhole.publish_message.publish_message,
                [
                    Argument("Input", U16(0)),
                    Argument("Input", U16(4)),
                    Argument("Result", U16(0)),
                    Argument("Input", U16(5)),
                ],
                []
            ]
        ]
    )


def get_signed_vaa():
    base_url = "https://wormhole-v2-testnet-api.certus.one/v1/signed_vaa/21/40440411a170b4842ae7dee4f4a7b7a58bc0a98566e998850a7bb87bf5dc05b9/"
    sequnce = "122"

    response = requests.get(base_url + sequnce)
    if 'vaaBytes' not in response.json():
        raise ValueError(f"Get sui-testnet signed vaa failed: {response.text}")

    vaa_bytes = response.json()['vaaBytes']
    vaa = base64.b64decode(vaa_bytes).hex()

    print(f"0x{vaa}")


if __name__ == '__main__':
    get_signed_vaa()