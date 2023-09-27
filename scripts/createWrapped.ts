import { createWrappedOnSolana, postVaaSolana } from "@certusone/wormhole-sdk";
import { Connection, Keypair } from "@solana/web3.js";
import * as fs from 'fs';
import * as path from 'path';

async function main() {
    const connection = new Connection("https://sparkling-wild-hexagon.solana-devnet.discover.quiknode.pro/2129a56170ae922c0d50ec36a09a6f683ab5a466/", "processed");

    const defaultPath = path.join(process.env.HOME, '.config/solana/id.json');
    const rawKey = JSON.parse(fs.readFileSync(defaultPath, 'utf-8'));
    const wallet = Keypair.fromSecretKey(Uint8Array.from(rawKey));

    const payerAddress = wallet.publicKey.toString();
    const SOL_BRIDGE_ADDRESS = "3u8hJUVTA4jH1wYAyUur7FFZVQ8H635K3tSHHF4ssjQ5"
    const SOL_TOKEN_BRIDGE_ADDRESS = "DZnkkTmCiFWfYTfT41X3Rd1kDgozqzxWaHqsw6W4x2oe"
    const signedVAA = "01000000000100c2cee42e36c6100055bb29971587571346e39e32c80e093d11367fb842c4fcfd3c87ed4d0781ea420e2750b8f6d0ce088cc3739dc904ce3d211a60634bb2ec0201651151b600000000001540440411a170b4842ae7dee4f4a7b7a58bc0a98566e998850a7bb87bf5dc05b900000000000000780002bda28aeb93874baba2273db9c92fb7b7fe2f412352e9633c0258978a32620a2300150a434f494e5f31300000000000000000000000000000000000000000000000000031302d446563696d616c20436f696e0000000000000000000000000000000000"

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

    // create wormhole wrapped token (mint and metadata) on solana
    const transaction = await createWrappedOnSolana(
        connection,
        SOL_BRIDGE_ADDRESS,
        SOL_TOKEN_BRIDGE_ADDRESS,
        payerAddress,
        Buffer.from(signedVAA, "hex")
    );

    // sign, send, and confirm transaction
    try {
        transaction.partialSign(wallet);
        const txid = await connection.sendRawTransaction(
            transaction.serialize()
        );

        console.log("txid: ", txid)
        await connection.confirmTransaction(txid);
    } catch (e) {
        console.log(e)
    }
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});