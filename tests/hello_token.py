import asyncio
import json

from pathlib import Path
from solana.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey

from hellotoken.instructions import (
    initialize,
    register_foreign_contract,
    redeem_wrapped_transfer_with_payload,
    redeem_native_transfer_with_payload,
    send_wrapped_tokens_with_payload,
    send_native_tokens_with_payload,
)
from hellotoken.program_id import PROGRAM_ID
from help import (
    deriveSenderConfigKey,
    deriveRedeemerConfigKey,
    deriveForeignContractKey,
    getTokenBridgeDerivedAccounts,
    deriveForeignEndPointKey,
    getRedeemWrappedTransferAccounts,
    getSendWrappedTransferAccounts,
    deriveTokenTransferMessageKey,
    ParsedVaa, getSendNativeTransferAccounts, getRedeemNativeTransferAccounts
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

    redeem_wrapped_accounts = getRedeemWrappedTransferAccounts(
        token_bridge_program_id,
        wormhole_program_id,
        PROGRAM_ID,
        payer.pubkey(),
        vaa
    )

    ix = redeem_wrapped_transfer_with_payload(
        args={
            "vaa_hash": parsed_vaa.hash
        },
        accounts={
            "payer": payer.pubkey(),
            "payer_token_account": redeem_wrapped_accounts["payer_token_key"],
            "config": redeem_wrapped_accounts["redeemer_config_key"],
            "foreign_contract": redeem_wrapped_accounts["foreign_contract_key"],
            "token_bridge_wrapped_mint": redeem_wrapped_accounts["token_bridge_wrapped_mint"],
            "recipient_token_account": redeem_wrapped_accounts["recipient_token_account"],
            "recipient": redeem_wrapped_accounts["recipient"],
            "tmp_token_account": redeem_wrapped_accounts["tmp_token_key"],
            "wormhole_program": redeem_wrapped_accounts["wormhole_program"],
            "token_bridge_program": redeem_wrapped_accounts["token_bridge_program"],
            "token_bridge_wrapped_meta": redeem_wrapped_accounts["token_bridge_wrapped_meta"],
            "token_bridge_config": redeem_wrapped_accounts["token_bridge_config"],
            "vaa": redeem_wrapped_accounts["vaa"],
            "token_bridge_claim": redeem_wrapped_accounts["token_bridge_claim"],
            "token_bridge_foreign_endpoint": redeem_wrapped_accounts["token_bridge_foreign_endpoint"],
            "token_bridge_mint_authority": redeem_wrapped_accounts["token_bridge_mint_authority"]
        },
    )

    tx = Transaction(fee_payer=payer.pubkey()).add(ix)

    tx_sig = await client.send_transaction(tx, payer)
    print(tx_sig)

    resp = await client.get_transaction(tx_sig.value)
    print(resp)

    await client.close()

async def hellotoken_redeem_native_transfer_with_payload(vaa: str):
    client = AsyncClient(rpc_url)
    await client.is_connected()

    payer = await get_payer()

    # wrapped sol mint
    wrapped_sol_mint = Pubkey.from_string("So11111111111111111111111111111111111111112")

    parsed_vaa = ParsedVaa.parse_vaa(vaa)

    redeem_native_accounts = getRedeemNativeTransferAccounts(
        token_bridge_program_id,
        wormhole_program_id,
        PROGRAM_ID,
        payer.pubkey(),
        vaa,
        wrapped_sol_mint
    )

    ix = redeem_native_transfer_with_payload(
        args={
            "vaa_hash": parsed_vaa.hash
        },
        accounts={
            "payer": payer.pubkey(),
            "payer_token_account": redeem_native_accounts["payer_token_account"],
            "config": redeem_native_accounts["redeemer_config"],
            "foreign_contract": redeem_native_accounts["foreign_contract"],
            "mint": wrapped_sol_mint,
            "recipient_token_account": redeem_native_accounts["recipient_token_account"],
            "recipient": redeem_native_accounts["recipient"],
            "tmp_token_account": redeem_native_accounts["tmp_token_account"],
            "wormhole_program": redeem_native_accounts["wormhole_program"],
            "token_bridge_program": redeem_native_accounts["token_bridge_program"],
            "token_bridge_config": redeem_native_accounts["token_bridge_config"],
            "vaa": redeem_native_accounts["vaa"],
            "token_bridge_claim": redeem_native_accounts["token_bridge_claim"],
            "token_bridge_foreign_endpoint": redeem_native_accounts["token_bridge_foreign_endpoint"],
            "token_bridge_custody": redeem_native_accounts["token_bridge_custody"],
            "token_bridge_custody_signer": redeem_native_accounts["token_bridge_custody_signer"]
        }
    )

    tx = Transaction(fee_payer=payer.pubkey()).add(ix)

    tx_sig = await client.send_transaction(tx, payer)
    print(tx_sig)

    resp = await client.get_transaction(tx_sig.value)
    print(resp)

    await client.close()


async def hellotoken_send_wrapped_tokens_with_payload():
    client = AsyncClient(rpc_url)
    await client.is_connected()

    payer = await get_payer()

    # sui-testnet
    recipient_chain = 21
    # coin10
    recipient_token = bytes.fromhex("bda28aeb93874baba2273db9c92fb7b7fe2f412352e9633c0258978a32620a23")
    # wrapper coin10
    coin10_from_account = Pubkey.from_string("H9FHrVoHSA8B1akWr4gvFHSb7MnDtr69kjjnD7BWnNmL")
    # send amount(decimals=8), 1 coin
    amount = 100000000
    # recipient
    recipient_address = bytes.fromhex("e76e8792889a2c3d6f7cf3b8b21be9c9f162ae98e1f218f23ac6d09e70931a2d")

    send_wrapped_accounts = getSendWrappedTransferAccounts(
        token_bridge_program_id,
        wormhole_program_id,
        PROGRAM_ID,
        recipient_chain,
        recipient_token
    )

    current_sequence = await client.get_account_info(send_wrapped_accounts["token_bridge_sequence"])

    next_seq = int.from_bytes(current_sequence.value.data, byteorder='little') + 1
    print(f"sequence={next_seq}")
    wormhole_message = deriveTokenTransferMessageKey(PROGRAM_ID, next_seq)

    ix = send_wrapped_tokens_with_payload(
        args={
            "batch_id": 0,
            "amount": amount,
            "recipient_address": list(recipient_address),
            "recipient_chain": recipient_chain
        },
        accounts={
            "payer": payer.pubkey(),
            "config": send_wrapped_accounts["send_config"],
            "foreign_contract": send_wrapped_accounts["foreign_contract"],
            "token_bridge_wrapped_mint": send_wrapped_accounts["token_bridge_wrapped_mint"],
            "from_token_account": coin10_from_account,
            "tmp_token_account": send_wrapped_accounts["tmp_token_account"],
            "wormhole_program": send_wrapped_accounts["wormhole_program"],
            "token_bridge_program": send_wrapped_accounts["token_bridge_program"],
            "token_bridge_wrapped_meta": send_wrapped_accounts["token_bridge_wrapped_meta"],
            "token_bridge_config": send_wrapped_accounts["token_bridge_config"],
            "token_bridge_authority_signer": send_wrapped_accounts["token_bridge_authority_signer"],
            "wormhole_bridge": send_wrapped_accounts["wormhole_bridge"],
            "wormhole_message": wormhole_message,
            "token_bridge_emitter": send_wrapped_accounts["token_bridge_emitter"],
            "token_bridge_sequence": send_wrapped_accounts["token_bridge_sequence"],
            "wormhole_fee_collector": send_wrapped_accounts["wormhole_fee_collector"]
        }
    )

    tx = Transaction(fee_payer=payer.pubkey()).add(ix)

    tx_sig = await client.send_transaction(tx, payer)
    print(tx_sig)

    resp = await client.get_transaction(tx_sig.value)
    print(resp)


    await client.close()

async def hellotoken_send_native_tokens_with_payload():
    client = AsyncClient(rpc_url)
    await client.is_connected()

    payer = await get_payer()

    # sui-testnet
    recipient_chain = 21
    # wrapped sol
    # recipient_token = bytes.fromhex("215a00f3162a83849a7d1d4ce982fa8ceda94fd9ab505d7f94452eece5feaf25")
    # wrapped sol mint
    wrapped_sol_mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
    # wrapped sol account
    wrapped_sol_account = Pubkey.from_string("6keZXUa7n3hoHkboSnzpGETANuwY43zWZC3FGrCPN1Gh")
    # send 1 wsol
    amount = 100000000
    # recipient
    recipient_address = bytes.fromhex("e76e8792889a2c3d6f7cf3b8b21be9c9f162ae98e1f218f23ac6d09e70931a2d")

    send_native_accounts = getSendNativeTransferAccounts(
        token_bridge_program_id,
        wormhole_program_id,
        PROGRAM_ID,
        recipient_chain,
        wrapped_sol_mint
    )

    current_sequence = await client.get_account_info(send_native_accounts["token_bridge_sequence"])

    next_seq = int.from_bytes(current_sequence.value.data, byteorder='little') + 1
    print(f"sequence={next_seq}")

    wormhole_message = deriveTokenTransferMessageKey(PROGRAM_ID, next_seq)

    ix = send_native_tokens_with_payload(
        args={
            "batch_id": 0,
            "amount": amount,
            "recipient_address": list(recipient_address),
            "recipient_chain": recipient_chain
        },
        accounts={
            "payer": payer.pubkey(),
            "config": send_native_accounts["send_config"],
            "foreign_contract": send_native_accounts["foreign_contract"],
            "mint": wrapped_sol_mint,
            "from_token_account": wrapped_sol_account,
            "tmp_token_account": send_native_accounts["tmp_token_account"],
            "wormhole_program": send_native_accounts["wormhole_program"],
            "token_bridge_program": send_native_accounts["token_bridge_program"],
            "token_bridge_config": send_native_accounts["token_bridge_config"],
            "token_bridge_custody": send_native_accounts["token_bridge_custody"],
            "token_bridge_authority_signer": send_native_accounts["token_bridge_authority_signer"],
            "token_bridge_custody_signer": send_native_accounts["token_bridge_custody_signer"],
            "wormhole_bridge": send_native_accounts["wormhole_bridge"],
            "wormhole_message": wormhole_message,
            "token_bridge_emitter": send_native_accounts["token_bridge_emitter"],
            "token_bridge_sequence": send_native_accounts["token_bridge_sequence"],
            "wormhole_fee_collector": send_native_accounts["wormhole_fee_collector"]
        }
    )

    tx = Transaction(fee_payer=payer.pubkey()).add(ix)

    tx_sig = await client.send_transaction(tx, payer)
    print(tx_sig)

    resp = await client.get_transaction(tx_sig.value)
    print(resp)


    await client.close()


vaa = "0x010000000001005deefe8dd16b7cb0b87c85c81a7ff60508454e9a5fb4ce3c28db6f8c5b1d0c752138bc97a9d372ab8617393402dc3ef37f67f38eb8adcaf49dbdc3a44d00a264006516a07900000000001540440411a170b4842ae7dee4f4a7b7a58bc0a98566e998850a7bb87bf5dc05b9000000000000007e00030000000000000000000000000000000000000000000000000000000000989298069b8857feab8184fb687f634618c035dac439dc1aeb3b5598a0f000000000010001ceda17841d79db34bd17721d2024343b5d9dd0320626958e10f4cf3d800a719e000135fbfedfe4ba06b311b86ae1d2064e08e583e6d550524307fc626648c4718c0c0138e121709ad96bd37a2f87022932336e9a290f62aef3d41dae00b1547c6f1938"

asyncio.run(hellotoken_redeem_native_transfer_with_payload(vaa))