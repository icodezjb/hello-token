from eth_utils import keccak
import json

from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.sysvar import RENT
from typing import Union
from base58 import b58encode
from spl.token.instructions import get_associated_token_address


def deriveWormholeEmitterKey(emitter_program_id: str):
    program_id = Pubkey.from_string(emitter_program_id)
    program_address, _nonce = Pubkey.find_program_address([b"emitter"], program_id)
    return program_address


def deriveEmitterSequenceKey(emitter: Pubkey, wormhole_program_id: str):
    program_id = Pubkey.from_string(wormhole_program_id)
    seed = [b"Sequence"]
    seed.append(bytes(emitter))
    program_address, _nonce = Pubkey.find_program_address(seed, program_id)

    return program_address


def deriveWormholeBridgeDataKey(wormhole_program_id: str):
    program_id = Pubkey.from_string(wormhole_program_id)
    program_address, _nonce = Pubkey.find_program_address([b"Bridge"], program_id)
    return program_address


def deriveFeeCollectorKey(wormhole_program_id: str):
    program_id = Pubkey.from_string(wormhole_program_id)
    program_address, _nonce = Pubkey.find_program_address([b"fee_collector"], program_id)
    return program_address


def deriveSenderConfigKey(hello_token_program_id: Union[str, Pubkey]):
    if isinstance(hello_token_program_id, str):
        program_id = Pubkey.from_string(hello_token_program_id)
    else:
        program_id = hello_token_program_id
    program_address, _nonce = Pubkey.find_program_address([b"sender"], program_id)
    return program_address


def deriveRedeemerConfigKey(hello_token_program_id: Union[str, Pubkey]):
    if isinstance(hello_token_program_id, str):
        program_id = Pubkey.from_string(hello_token_program_id)
    else:
        program_id = hello_token_program_id
    program_address, _nonce = Pubkey.find_program_address([b"redeemer"], program_id)
    return program_address


def deriveForeignContractKey(hello_token_program_id: Union[str, Pubkey], chain: int):
    if isinstance(hello_token_program_id, str):
        program_id = Pubkey.from_string(hello_token_program_id)
    else:
        program_id = hello_token_program_id

    seed = [b"foreign_contract"]
    seed.append(chain.to_bytes(length=2, byteorder="little", signed=False))
    program_address, _nonce = Pubkey.find_program_address(
        seed,
        program_id
    )
    return program_address

def deriveTokenTransferMessageKey(
        hello_token_program_id: Union[str, Pubkey],
        next_seq: int
):
    if isinstance(hello_token_program_id, str):
        program_id = Pubkey.from_string(hello_token_program_id)
    else:
        program_id = hello_token_program_id

    seed = [b"bridged"]
    seed.append(next_seq.to_bytes(length=8, byteorder="little", signed=False))

    program_address, _nonce = Pubkey.find_program_address(
        seed,
        program_id
    )
    return program_address


def deriveForeignEndPointKey(
        token_bridge_program_id: str,
        chain: int,
        foreign_contract: Pubkey
):
    assert chain != 1, "emitterChain == CHAIN_ID_SOLANA cannot exist as foreign token bridge emitter"

    program_id = Pubkey.from_string(token_bridge_program_id)

    seed = [chain.to_bytes(length=2, byteorder="big", signed=False)]
    seed.append(bytes(foreign_contract))

    program_address, _nonce = Pubkey.find_program_address(
        seed,
        program_id
    )
    return program_address


def getEmitterKeys(token_bridge_program_id: str, wormhole_program_id: str):
    emitter = deriveWormholeEmitterKey(token_bridge_program_id)
    sequence = deriveEmitterSequenceKey(emitter, wormhole_program_id)

    return emitter, sequence


def getWormholeDerivedAccounts(
        token_bridge_program_id: str,
        wormhole_program_id: str
):
    token_bridge_emitter, token_bridge_sequence = getEmitterKeys(token_bridge_program_id, wormhole_program_id)
    wormhole_bridge = deriveWormholeBridgeDataKey(wormhole_program_id)
    wormhole_fee_collector = deriveFeeCollectorKey(wormhole_program_id)

    return wormhole_bridge, token_bridge_emitter, wormhole_fee_collector, token_bridge_sequence


def deriveTokenBridgeConfigKey(token_bridge_program_id: str):
    program_id = Pubkey.from_string(token_bridge_program_id)
    program_address, _nonce = Pubkey.find_program_address([b"config"], program_id)
    return program_address


def deriveAuthoritySignerKey(token_bridge_program_id: str):
    program_id = Pubkey.from_string(token_bridge_program_id)
    program_address, _nonce = Pubkey.find_program_address([b"authority_signer"], program_id)
    return program_address

def deriveCustodyKey(
        token_bridge_program_id: str,
        native_mint: Pubkey,
):
    program_id = Pubkey.from_string(token_bridge_program_id)
    program_address, _nonce = Pubkey.find_program_address([bytes(native_mint)], program_id)
    return program_address

def deriveCustodySignerKey(token_bridge_program_id: str):
    program_id = Pubkey.from_string(token_bridge_program_id)
    program_address, _nonce = Pubkey.find_program_address([b"custody_signer"], program_id)
    return program_address


def deriveMintAuthorityKey(token_bridge_program_id: str):
    program_id = Pubkey.from_string(token_bridge_program_id)
    program_address, _nonce = Pubkey.find_program_address([b"mint_signer"], program_id)
    return program_address


def getTokenBridgeDerivedAccounts(
        token_bridge_program_id: str,
        wormhole_program_id: str
):
    wormhole_accounts = getWormholeDerivedAccounts(token_bridge_program_id, wormhole_program_id)

    return {
        "token_bridge_config": deriveTokenBridgeConfigKey(token_bridge_program_id),
        "token_bridge_authority_signer": deriveAuthoritySignerKey(token_bridge_program_id),
        "token_bridge_custody_signer": deriveCustodySignerKey(token_bridge_program_id),
        "token_bridge_mint_authority": deriveMintAuthorityKey(token_bridge_program_id),
        "wormhole_bridge": wormhole_accounts[0],
        "token_bridge_emitter": wormhole_accounts[1],
        "wormhole_fee_collector": wormhole_accounts[2],
        "token_bridge_sequence": wormhole_accounts[3]
    }

def deriveWrappedMintKey(
        token_bridge_program_id: str,
        token_chain: int,
        token_address: Union[str, bytes]
):
    assert token_chain != 1, "tokenChain == CHAIN_ID_SOLANA does not have wrapped mint key"

    if isinstance(token_address, str):
        token_address = bytes.fromhex(token_address.replace("0x", ""))

    program_id = Pubkey.from_string(token_bridge_program_id)

    seed = [b"wrapped"]
    seed.append(token_chain.to_bytes(length=2, byteorder="big", signed=False))
    seed.append(token_address)

    program_address, _nonce = Pubkey.find_program_address(seed, program_id)
    return program_address

def derivePostedVaaKey(
        wormhole_program_id: str,
        hash: Union[str, bytes]
):
    if isinstance(hash, str):
        hash = bytes.fromhex(hash.replace("0x", ""))

    program_id = Pubkey.from_string(wormhole_program_id)

    seed = [b"PostedVAA"]
    seed.append(hash)

    program_address, _nonce = Pubkey.find_program_address(seed, program_id)
    return program_address

def deriveGuardianSetKey(
        wormhole_program_id: str,
        index: int
):
    program_id = Pubkey.from_string(wormhole_program_id)

    seed = [b"GuardianSet"]
    seed.append(index.to_bytes(length=4, byteorder="big", signed=False))

    program_address, _nonce = Pubkey.find_program_address(seed, program_id)
    return program_address

def deriveClaimKey(
        token_bridge_program_id: str,
        emitter_address: Union[str, bytes],
        emitter_chain: int,
        sequence: int
):
    if isinstance(emitter_address, str):
        emitter_address = bytes.fromhex(emitter_address.replace("0x", ""))

    assert len(emitter_address) == 32, "address.length != 32"

    program_id = Pubkey.from_string(token_bridge_program_id)

    seed = [emitter_address]
    seed.append(emitter_chain.to_bytes(length=2, byteorder="big", signed=False))
    seed.append(sequence.to_bytes(length=8, byteorder="big", signed=False))

    program_address, _nonce = Pubkey.find_program_address(seed, program_id)
    return program_address

def deriveWrappedMetaKey(
        token_bridge_program_id: str,
        mint_key: Pubkey
):
    program_id = Pubkey.from_string(token_bridge_program_id)

    seed = [b"meta"]
    seed.append(bytes(mint_key))

    program_address, _nonce = Pubkey.find_program_address(seed, program_id)
    return program_address

def deriveTmpTokenAccountKey(
        hello_token_program_id: Union[str, Pubkey],
        wrapped_mint: Pubkey
):
    if isinstance(hello_token_program_id, str):
        program_id = Pubkey.from_string(hello_token_program_id)
    else:
        program_id = hello_token_program_id

    seed = [b"tmp"]
    seed.append(bytes(wrapped_mint))

    program_address, _nonce = Pubkey.find_program_address(seed, program_id)
    return program_address

def getRedeemWrappedTransferAccounts(
        token_bridge_program_id: str,
        wormhole_program_id: str,
        hello_token_program_id: str,
        payer: Pubkey,
        vaa: Union[str, bytes],
):
    parsed_vaa = ParsedVaa.parse_vaa(vaa)
    token_transfer = TokenTransfer.parse_token_transfer_payload(parsed_vaa.payload)

    wrapped_mint_key = deriveWrappedMintKey(
        token_bridge_program_id,
        token_transfer.token_chain,
        token_transfer.token_address
    )

    tmp_token_key = deriveTmpTokenAccountKey(
        hello_token_program_id,
        wrapped_mint_key
    )

    recipient_key = Pubkey.from_bytes(token_transfer.recipient())

    recipient_token_key = get_associated_token_address(recipient_key, wrapped_mint_key)
    payer_token_key = get_associated_token_address(payer, wrapped_mint_key)

    redeemer_config_key = deriveRedeemerConfigKey(hello_token_program_id)
    foreign_contract_key = deriveForeignContractKey(
        hello_token_program_id,
        parsed_vaa.emitter_chain
    )

    return {
        "vaa": derivePostedVaaKey(wormhole_program_id, parsed_vaa.hash),
        "tmp_token_key": tmp_token_key,
        "redeemer_config_key": redeemer_config_key,
        "payer_token_key": payer_token_key,
        "recipient": recipient_key,
        "recipient_token_key": recipient_token_key,
        "foreign_contract_key": foreign_contract_key,
        "token_bridge_config": deriveTokenBridgeConfigKey(token_bridge_program_id),
        "token_bridge_claim": deriveClaimKey(
            token_bridge_program_id,
            parsed_vaa.emitter_address,
            parsed_vaa.emitter_chain,
            parsed_vaa.sequence
        ),
        "token_bridge_foreign_endpoint": deriveForeignEndPointKey(
            token_bridge_program_id,
            parsed_vaa.emitter_chain,
            parsed_vaa.emitter_address
        ),
        "token_bridge_wrapped_mint": wrapped_mint_key,
        "token_bridge_wrapped_meta": deriveWrappedMetaKey(
            token_bridge_program_id,
            wrapped_mint_key
        ),
        "token_bridge_mint_authority": deriveMintAuthorityKey(token_bridge_program_id),
        "wormhole_program": Pubkey.from_string(wormhole_program_id),
        "token_bridge_program": Pubkey.from_string(token_bridge_program_id)
    }

def getRedeemNativeTransferAccounts(
        token_bridge_program_id: str,
        wormhole_program_id: str,
        hello_token_program_id: str,
        payer: Pubkey,
        vaa: Union[str, bytes],
        native_mint: Pubkey
):
    parsed_vaa = ParsedVaa.parse_vaa(vaa)
    token_transfer = TokenTransfer.parse_token_transfer_payload(parsed_vaa.payload)

    tmp_token_key = deriveTmpTokenAccountKey(
        hello_token_program_id,
        native_mint
    )

    recipient_key = Pubkey.from_bytes(token_transfer.recipient())

    recipient_token_key = get_associated_token_address(recipient_key, native_mint)
    payer_token_key = get_associated_token_address(payer, native_mint)

    redeemer_config_key = deriveRedeemerConfigKey(hello_token_program_id)
    foreign_contract_key = deriveForeignContractKey(
        hello_token_program_id,
        parsed_vaa.emitter_chain
    )


    return {
        "payer_token_account": payer_token_key,
        "redeemer_config": redeemer_config_key,
        "foreign_contract": foreign_contract_key,
        "recipient_token_account": recipient_token_key,
        "recipient": recipient_key,
        "tmp_token_account": tmp_token_key,
        "wormhole_program": Pubkey.from_string(wormhole_program_id),
        "token_bridge_program": Pubkey.from_string(token_bridge_program_id),
        "token_bridge_config": deriveTokenBridgeConfigKey(token_bridge_program_id),
        "vaa": derivePostedVaaKey(wormhole_program_id, parsed_vaa.hash),
        "token_bridge_claim": deriveClaimKey(
            token_bridge_program_id,
            parsed_vaa.emitter_address,
            parsed_vaa.emitter_chain,
            parsed_vaa.sequence
        ),
        "token_bridge_foreign_endpoint": deriveForeignEndPointKey(
            token_bridge_program_id,
            parsed_vaa.emitter_chain,
            parsed_vaa.emitter_address
        ),
        "token_bridge_custody": deriveCustodyKey(
            token_bridge_program_id,
            native_mint
        ),
        "token_bridge_custody_signer": deriveCustodySignerKey(
            token_bridge_program_id
        )
    }

def getSendWrappedTransferAccounts(
        token_bridge_program_id: str,
        wormhole_program_id: str,
        hello_token_program_id: str,
        recipient_chain: int,
        recipient_token: bytes,
):
    wrapped_mint_key = deriveWrappedMintKey(
        token_bridge_program_id,
        recipient_chain,
        recipient_token
    )

    tmp_token_key = deriveTmpTokenAccountKey(
        hello_token_program_id,
        wrapped_mint_key
    )

    send_config_key = deriveSenderConfigKey(hello_token_program_id)

    foreign_contract_key = deriveForeignContractKey(
        hello_token_program_id,
        recipient_chain
    )

    token_bridge_emitter, token_bridge_sequence = getEmitterKeys(
        token_bridge_program_id,
        wormhole_program_id
    )

    bridge_data_key = deriveWormholeBridgeDataKey(wormhole_program_id)
    fee_collector_key = deriveFeeCollectorKey(wormhole_program_id)

    authority_signer_key = deriveAuthoritySignerKey(token_bridge_program_id)

    return {
        "send_config": send_config_key,
        "foreign_contract": foreign_contract_key,
        "token_bridge_wrapped_mint": wrapped_mint_key,
        "tmp_token_account": tmp_token_key,
        "wormhole_program": Pubkey.from_string(wormhole_program_id),
        "token_bridge_program": Pubkey.from_string(token_bridge_program_id),
        "token_bridge_wrapped_meta": deriveWrappedMetaKey(
            token_bridge_program_id,
            wrapped_mint_key
        ),
        "token_bridge_config": deriveTokenBridgeConfigKey(token_bridge_program_id),
        "token_bridge_authority_signer": authority_signer_key,
        "wormhole_bridge": bridge_data_key,
        "token_bridge_emitter": token_bridge_emitter,
        "token_bridge_sequence": token_bridge_sequence,
        "wormhole_fee_collector": fee_collector_key,
    }

def getSendNativeTransferAccounts(
        token_bridge_program_id: str,
        wormhole_program_id: str,
        hello_token_program_id: str,
        recipient_chain: int,
        native_mint_key: Pubkey
):
    tmp_token_key = deriveTmpTokenAccountKey(
        hello_token_program_id,
        native_mint_key
    )

    send_config_key = deriveSenderConfigKey(hello_token_program_id)

    foreign_contract_key = deriveForeignContractKey(
        hello_token_program_id,
        recipient_chain
    )

    token_bridge_emitter, token_bridge_sequence = getEmitterKeys(
        token_bridge_program_id,
        wormhole_program_id
    )

    bridge_data_key = deriveWormholeBridgeDataKey(wormhole_program_id)
    fee_collector_key = deriveFeeCollectorKey(wormhole_program_id)

    authority_signer_key = deriveAuthoritySignerKey(token_bridge_program_id)

    token_bridge_config = deriveTokenBridgeConfigKey(token_bridge_program_id)
    token_bridge_custody = deriveCustodyKey(
        token_bridge_program_id,
        native_mint_key
    )

    custody_signer_key = deriveCustodySignerKey(token_bridge_program_id)

    return {
        "send_config": send_config_key,
        "foreign_contract": foreign_contract_key,
        "tmp_token_account": tmp_token_key,
        "wormhole_program": Pubkey.from_string(wormhole_program_id),
        "token_bridge_program": Pubkey.from_string(token_bridge_program_id),
        "token_bridge_config": token_bridge_config,
        "token_bridge_custody": token_bridge_custody,
        "token_bridge_authority_signer": authority_signer_key,
        "token_bridge_custody_signer": custody_signer_key,
        "wormhole_bridge": bridge_data_key,
        "token_bridge_emitter": token_bridge_emitter,
        "token_bridge_sequence": token_bridge_sequence,
        "wormhole_fee_collector": fee_collector_key
    }

class ParsedVaa:
    def __init__(
            self,
            version,
            guardian_set_index,
            guardian_signatures,
            timestamp,
            nonce,
            emitter_chain,
            emitter_address,
            sequence,
            consistency_level,
            payload,
            hash
    ):
        self.version = version
        self.guardian_set_index = guardian_set_index
        self.guardian_signatures = guardian_signatures
        self.timestamp = timestamp
        self.nonce = nonce
        self.emitter_chain = emitter_chain
        self.emitter_address = emitter_address
        self.sequence = sequence
        self.consistency_level = consistency_level
        self.payload = payload
        self.hash = hash

    def __str__(self):
        return json.dumps(self.format_json(), indent=2)

    def format_json(self):
        return {
            "version": self.version,
            "guardianSetIndex": self.guardian_set_index,
            "guardianSignatures": [
                {
                    "index": g["index"],
                    "signature": "0x" + g["signature"].hex()
                }
                for g in self.guardian_signatures
            ],
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "emitterChain": self.emitter_chain,
            "emitterAddress": "0x" + self.emitter_address.hex(),
            "sequence": self.sequence,
            "consistencyLevel": self.consistency_level,
            "payload": "0x" + self.payload.hex(),
            "hash": "0x" + self.hash.hex(),
        }

    @classmethod
    def parse_vaa(cls, vaa: Union[bytes, str]):
        if isinstance(vaa, str):
            signed_vaa = bytearray(bytes.fromhex(vaa.replace("0x", "")))
        else:
            signed_vaa = bytearray(vaa)

        sig_start = 6
        num_signers = signed_vaa[5]
        sig_length = 66

        guardian_signatures = []
        for i in range(num_signers):
            start = sig_start + i * sig_length
            guardian_signatures.append({
                "index": signed_vaa[start],
                "signature": bytes(signed_vaa[start + 1:start + 66]),
            })

        body = signed_vaa[sig_start + sig_length * num_signers:]

        return ParsedVaa(
            signed_vaa[0],
            int.from_bytes(signed_vaa[1:5], byteorder="big"),
            guardian_signatures,
            int.from_bytes(body[0:4], byteorder="big"),
            int.from_bytes(body[4:8], byteorder="big"),
            int.from_bytes(body[8:10], byteorder="big"),
            bytes(body[10:42]),
            int.from_bytes(body[42:50], byteorder="big"),
            body[50],
            bytes(body[51:]),
            keccak(body)
        )


class TokenTransfer:
    Transfer = 1
    AttestMeta = 2
    TransferWithPayload = 3

    def __init__(
            self,
            payload_type,
            amount,
            token_address,
            token_chain,
            redeemer,
            redeemer_chain,
            fee,
            from_emitter,
            token_transfer_payload
    ):
        self.payload_type = payload_type
        self.amount = amount
        self.token_address = token_address
        self.token_chain = token_chain
        self.redeemer = redeemer
        self.redeemer_chain = redeemer_chain
        self.fee = fee
        self.from_emitter = from_emitter
        self.token_transfer_payload = token_transfer_payload

    def __str__(self):
        return json.dumps(self.format_json(), indent=2)

    def format_json(self):
        return {
            "payloadType": self.payload_type,
            "amount": self.amount,
            "tokenAddress": "0x"+self.token_address.hex(),
            "tokenChain": self.token_chain,
            "redeemer": b58encode(self.redeemer).decode("utf-8") if self.redeemer_chain == 1 else "0x"+self.redeemer.hex(),
            "redeemerChain": self.redeemer_chain,
            "fee": self.fee,
            "fromEmitter": "0x"+self.from_emitter.hex(),
            "tokenTransferPayload": "0x"+self.token_transfer_payload.hex()
        }

    @classmethod
    def parse_token_transfer_payload(cls, payload: Union[bytes, str]):
        if isinstance(payload, str):
            payload = bytes.fromhex(payload.replace("0x", ""))

        payload_type = payload[0]
        if payload_type not in (cls.Transfer, cls.TransferWithPayload):
            raise ValueError("not token bridge transfer VAA")

        amount_bytes = payload[1:33]
        amount = int.from_bytes(amount_bytes, byteorder='big')

        token_address = payload[33:65]

        token_chain_bytes = payload[65:67]
        token_chain = int.from_bytes(token_chain_bytes, byteorder='big')

        redeemer = payload[67:99]

        redeemer_chain_bytes = payload[99:101]
        redeemer_chain = int.from_bytes(redeemer_chain_bytes, byteorder='big')

        if payload_type == cls.Transfer:
            fee_bytes = payload[101:133]
            fee = int.from_bytes(fee_bytes, byteorder='big')
        else:
            fee = None

        if payload_type == cls.TransferWithPayload:
            from_emitter = payload[101:133]
        else:
            from_emitter = None

        token_transfer_payload = payload[133:]

        return TokenTransfer(
            payload_type,
            amount,
            token_address,
            token_chain,
            redeemer,
            redeemer_chain,
            fee,
            from_emitter,
            token_transfer_payload
        )

    def recipient(self):
        assert len(self.token_transfer_payload) == 33, "decode recipient fail"

        print(f"recipient: {b58encode(self.token_transfer_payload[1:]).decode()}")

        return self.token_transfer_payload[1:]


def parseTokenTransferVaa(vaa: Union[bytes, str]):
    parsed = ParsedVaa.parse_vaa(vaa)
    token_transfer = TokenTransfer.parse_token_transfer_payload(parsed.payload)

    print(parsed)
    print(token_transfer)

    return parsed, token_transfer



if __name__ == '__main__':
    parseTokenTransferVaa(
        "0x01000000000100081b53f79da4b1b12dbfaee9ce88a1ec7f4b51cfb38832e9ae37da238f5be26b08fd93d573d500f7974bc463e7cbaa6fc2a3661591567c3c2ec72f52c5354f98006511d13900000000001540440411a170b4842ae7dee4f4a7b7a58bc0a98566e998850a7bb87bf5dc05b9000000000000007a000300000000000000000000000000000000000000000000000000000002540be400bda28aeb93874baba2273db9c92fb7b7fe2f412352e9633c0258978a32620a230015ceda17841d79db34bd17721d2024343b5d9dd0320626958e10f4cf3d800a719e000135fbfedfe4ba06b311b86ae1d2064e08e583e6d550524307fc626648c4718c0c0138e121709ad96bd37a2f87022932336e9a290f62aef3d41dae00b1547c6f1938")
