import requests
import base64
from help import ParsedVaa

def get_sui_signed_vaa(sequence: str):
    base_url = "https://wormhole-v2-testnet-api.certus.one/v1/signed_vaa/21/40440411a170b4842ae7dee4f4a7b7a58bc0a98566e998850a7bb87bf5dc05b9/"

    response = requests.get(base_url + sequence)
    if 'vaaBytes' not in response.json():
        raise ValueError(f"Get sui-testnet signed vaa failed: {response.text}")

    vaa_bytes = response.json()['vaaBytes']
    vaa = base64.b64decode(vaa_bytes).hex()

    return vaa

def get_solana_signed_vaa(sequence: str):
    base_url = "https://wormhole-v2-testnet-api.certus.one/v1/signed_vaa/1/3b26409f8aaded3f5ddca184695aa6a0fa829b0c85caf84856324896d214ca98/"

    response = requests.get(base_url + sequence)
    if 'vaaBytes' not in response.json():
        raise ValueError(f"Get sui-testnet signed vaa failed: {response.text}")

    vaa_bytes = response.json()['vaaBytes']
    vaa = base64.b64decode(vaa_bytes).hex()

    return vaa

def parse_coin_meta(vaa: str):
    v = ParsedVaa.parse_vaa(vaa)
    print(f"tokenAddress={v.payload[1:33].hex()}")
    print(f"tokenChain={int.from_bytes(v.payload[33:35], byteorder='big')}")
    print(f"decimals={int(v.payload[35])}")
    print(f"symbol={v.payload[36:68].decode('utf-8')}")
    print(f"name={v.payload[68:100].decode('utf-8')}")



if __name__ == '__main__':
    print(get_sui_signed_vaa("126"))
    # print((get_solana_signed_vaa("25487")))