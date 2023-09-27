import {Connection, Keypair, PublicKey} from "@solana/web3.js";
import { getOrCreateAssociatedTokenAccount } from "@solana/spl-token"
import * as fs from 'fs';
import * as path from 'path';


async function main() {
    const connection = new Connection("https://sparkling-wild-hexagon.solana-devnet.discover.quiknode.pro/2129a56170ae922c0d50ec36a09a6f683ab5a466/", "processed");

    const defaultPath = path.join(process.env.HOME, '.config/solana/id.json');
    const rawKey = JSON.parse(fs.readFileSync(defaultPath, 'utf-8'));
    const wallet = Keypair.fromSecretKey(Uint8Array.from(rawKey));

    const payerAddress = wallet.publicKey.toString();
    const wrappedMintKey = new PublicKey("AwcKdvJMfwYWTGY4TJzX8XgjY8kk97izi7zrxTseWTAT")

    console.log("payer: ", payerAddress)

    const associatedTokenAccount = await getOrCreateAssociatedTokenAccount(
        connection,
        wallet,
        wrappedMintKey,
        wallet.publicKey
    )

    console.log("associatedTokenAccount: ", associatedTokenAccount.address.toBase58())
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});