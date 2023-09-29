import { postVaaSolana } from "@certusone/wormhole-sdk";
import { Connection, Keypair } from "@solana/web3.js";
import path from "path";
import fs from "fs";

async function main() {
    const connection = new Connection("https://sparkling-wild-hexagon.solana-devnet.discover.quiknode.pro/2129a56170ae922c0d50ec36a09a6f683ab5a466/", "processed");

    const defaultPath = path.join(process.env.HOME, '.config/solana/id.json');
    const rawKey = JSON.parse(fs.readFileSync(defaultPath, 'utf-8'));
    const wallet = Keypair.fromSecretKey(Uint8Array.from(rawKey));

    const payerAddress = wallet.publicKey.toString();
    const SOL_BRIDGE_ADDRESS = "3u8hJUVTA4jH1wYAyUur7FFZVQ8H635K3tSHHF4ssjQ5"
    const signedVAA = "010000000001005deefe8dd16b7cb0b87c85c81a7ff60508454e9a5fb4ce3c28db6f8c5b1d0c752138bc97a9d372ab8617393402dc3ef37f67f38eb8adcaf49dbdc3a44d00a264006516a07900000000001540440411a170b4842ae7dee4f4a7b7a58bc0a98566e998850a7bb87bf5dc05b9000000000000007e00030000000000000000000000000000000000000000000000000000000000989298069b8857feab8184fb687f634618c035dac439dc1aeb3b5598a0f000000000010001ceda17841d79db34bd17721d2024343b5d9dd0320626958e10f4cf3d800a719e000135fbfedfe4ba06b311b86ae1d2064e08e583e6d550524307fc626648c4718c0c0138e121709ad96bd37a2f87022932336e9a290f62aef3d41dae00b1547c6f1938"

    await postVaaSolana(
        connection,
        async (transaction) => {
            transaction.partialSign(wallet);
            return transaction;
        },
        SOL_BRIDGE_ADDRESS,
        payerAddress,
        Buffer.from(signedVAA, "hex")
    );

    console.log("payer: ", payerAddress)
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});