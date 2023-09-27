import asyncio
import json

from pathlib import Path
from solana.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from spl.token.instructions import get_associated_token_address

from hellotoken.instructions import (
    initialize,
    register_foreign_contract,
    redeem_wrapped_transfer_with_payload,
    send_wrapped_tokens_with_payload,
)
from hellotoken.program_id import PROGRAM_ID
from help import (
    deriveSenderConfigKey,
    deriveRedeemerConfigKey,
    deriveForeignContractKey,
    getTokenBridgeDerivedAccounts,
    deriveForeignEndPointKey,
    getCompleteTransferWrappedAccounts,
    ParsedVaa, TokenTransfer, deriveTmpTokenAccountKey, deriveWrappedMintKey
)

# solana-devnet
rpc_url = "https://api.devnet.solana.com"
wormhole_program_id = "3u8hJUVTA4jH1wYAyUur7FFZVQ8H635K3tSHHF4ssjQ5"
token_bridge_program_id = "DZnkkTmCiFWfYTfT41X3Rd1kDgozqzxWaHqsw6W4x2oe"

async def get_payer():
    default_path = Path.home().joinpath(".config/solana/id.json")
    with open(default_path, "r") as file:
        raw_key = json.load(file)

    payer = Keypair.from_bytes(bytes(raw_key))

    print(f"payer={payer.pubkey()}")

    return payer


async def hellotoken_initialize():
    client = AsyncClient(rpc_url)
    await client.is_connected()

    payer = await get_payer()

    send_config_key = deriveSenderConfigKey(PROGRAM_ID)
    redeemer_config_key = deriveRedeemerConfigKey(PROGRAM_ID)

    token_bridge_accounts = getTokenBridgeDerivedAccounts(
        token_bridge_program_id,
        wormhole_program_id
    )

    ix = initialize(
        args={
            "relayer_fee": 10,
            "relayer_fee_precision": 100000
        },
        accounts={
            "owner": payer.pubkey(),
            "sender_config": send_config_key,
            "redeemer_config": redeemer_config_key,
            "wormhole_program": Pubkey.from_string(wormhole_program_id),
            "token_bridge_program": Pubkey.from_string(token_bridge_program_id),
            "token_bridge_config": token_bridge_accounts["token_bridge_config"],
            "token_bridge_authority_signer": token_bridge_accounts["token_bridge_authority_signer"],
            "token_bridge_custody_signer": token_bridge_accounts["token_bridge_custody_signer"],
            "token_bridge_mint_authority": token_bridge_accounts["token_bridge_mint_authority"],
            "wormhole_bridge": token_bridge_accounts["wormhole_bridge"],
            "token_bridge_emitter": token_bridge_accounts["token_bridge_emitter"],
            "wormhole_fee_collector": token_bridge_accounts["wormhole_fee_collector"],
            "token_bridge_sequence": token_bridge_accounts["token_bridge_sequence"],
        },
    )

    tx = Transaction(fee_payer=payer.pubkey()).add(ix)

    tx_sig = await client.send_transaction(tx, payer)
    print(tx_sig)

    resp = await client.get_transaction(tx_sig.value)
    print(resp)

    await client.close()


async def hellotoken_register_foreign_contract():
    client = AsyncClient(rpc_url)
    await client.is_connected()

    payer = await get_payer()

    send_config_key = deriveSenderConfigKey(PROGRAM_ID)

    chain_id_sui = 21
    token_bridge_emitter_sui = bytes.fromhex("40440411a170b4842ae7dee4f4a7b7a58bc0a98566e998850a7bb87bf5dc05b9")
    hello_emitter_sui = bytes.fromhex("35fbfedfe4ba06b311b86ae1d2064e08e583e6d550524307fc626648c4718c0c")


    foreign_contract_key = deriveForeignContractKey(PROGRAM_ID, chain_id_sui)
    foreign_endpoint_key = deriveForeignEndPointKey(
        token_bridge_program_id,
        chain_id_sui,
        Pubkey.from_bytes(token_bridge_emitter_sui)
    )

    print(foreign_endpoint_key)

    ix = register_foreign_contract(
        args={
            "chain": chain_id_sui,
            "address": list(hello_emitter_sui)
        },
        accounts={
            "owner": payer.pubkey(),
            "config": send_config_key,
            "foreign_contract": foreign_contract_key,
            "token_bridge_foreign_endpoint": foreign_endpoint_key,
            "token_bridge_program": Pubkey.from_string(token_bridge_program_id)
        },
    )

    tx = Transaction(fee_payer=payer.pubkey()).add(ix)

    tx_sig = await client.send_transaction(tx, payer)
    print(tx_sig)

    resp = await client.get_transaction(tx_sig.value)
    print(resp)

    await client.close()


async def hellotoken_redeem_wrapped_transfer_with_payload(vaa: str):
    client = AsyncClient(rpc_url)
    await client.is_connected()

    payer = await get_payer()

    parsed_vaa = ParsedVaa.parse_vaa(vaa)
    token_transfer = TokenTransfer.parse_token_transfer_payload(parsed_vaa.payload)

    wrapped_mint_key = deriveWrappedMintKey(
        token_bridge_program_id,
        token_transfer.token_chain,
        token_transfer.token_address
    )

    tmp_token_key = deriveTmpTokenAccountKey(
        PROGRAM_ID,
        wrapped_mint_key
    )

    token_bridge_accounts = getCompleteTransferWrappedAccounts(
        token_bridge_program_id,
        wormhole_program_id,
        payer.pubkey(),
        vaa,
        tmp_token_key
    )

    assert token_bridge_accounts["token_bridge_wrapped_mint"] == wrapped_mint_key

    recipient = token_transfer.recipient()

    recipient_token_key = get_associated_token_address(
        Pubkey.from_bytes(recipient),
        token_bridge_accounts["token_bridge_wrapped_mint"]
    )

    print(f"recipient_token_key: {recipient_token_key}")

    payer_token_key = get_associated_token_address(
        token_bridge_accounts["payer"],
        token_bridge_accounts["token_bridge_wrapped_mint"]
    )
    redeemer_config_key = deriveRedeemerConfigKey(PROGRAM_ID)

    foreign_contract_key = deriveForeignContractKey(
        PROGRAM_ID,
        parsed_vaa.emitter_chain
    )

    print(f"mint_key: {wrapped_mint_key}")

    ix = redeem_wrapped_transfer_with_payload(
        args={
            "vaa_hash": parsed_vaa.hash
        },
        accounts={
            "payer": token_bridge_accounts["payer"],
            "payer_token_account": payer_token_key,
            "config": redeemer_config_key,
            "foreign_contract": foreign_contract_key,
            "token_bridge_wrapped_mint": token_bridge_accounts["token_bridge_wrapped_mint"],
            "recipient_token_account": recipient_token_key,
            "recipient": Pubkey.from_bytes(recipient),
            "tmp_token_account": tmp_token_key,
            "wormhole_program": token_bridge_accounts["wormhole_program"],
            "token_bridge_program": token_bridge_accounts["token_bridge_program"],
            "token_bridge_wrapped_meta": token_bridge_accounts["token_bridge_wrapped_meta"],
            "token_bridge_config": token_bridge_accounts["token_bridge_config"],
            "vaa": token_bridge_accounts["vaa"],
            "token_bridge_claim": token_bridge_accounts["token_bridge_claim"],
            "token_bridge_foreign_endpoint": token_bridge_accounts["token_bridge_foreign_endpoint"],
            "token_bridge_mint_authority": token_bridge_accounts["token_bridge_mint_authority"]
        },
    )

    tx = Transaction(fee_payer=payer.pubkey()).add(ix)

    tx_sig = await client.send_transaction(tx, payer)
    print(tx_sig)

    resp = await client.get_transaction(tx_sig.value)
    print(resp)

    await client.close()


asyncio.run(get_payer())