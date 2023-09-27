
module hello_token::entry {
    // Sui dependencies.
    use sui::coin::Coin;
    use sui::tx_context::TxContext;
    use sui::sui::SUI;
    use sui::clock::Clock;

    // Token Bridge dependencies.
    use token_bridge::state::{State as TokenBridgeState, verified_asset};
    use token_bridge::transfer_tokens_with_payload::transfer_tokens_with_payload;
    use token_bridge::vaa::verify_only_once;
    use token_bridge::complete_transfer_with_payload::authorize_transfer;

    // Wormhole dependencies.
    use wormhole::publish_message;
    use wormhole::state::State as WormholeState;
    use wormhole::vaa::parse_and_verify;

    // Hello Token dependencies.
    use hello_token::state::State;
    use hello_token::transfer::{
        send_tokens_with_payload, redeem_transfer_with_payload
    };

    public entry fun external_send_tokens_with_payload<C>(
        t_state: &State,
        coins: Coin<C>,
        token_bridge_state: &mut TokenBridgeState,
        target_chain: u16,
        target_recipient: address,
        nonce: u32,
        wormhole_state: &mut WormholeState,
        message_fee: Coin<SUI>,
        the_clock: &Clock,
        ctx: & TxContext
    ) {
        let asset_info = verified_asset<C>(token_bridge_state);
        let transfer_ticket = send_tokens_with_payload<C>(
            t_state,
            coins,
            asset_info,
            target_chain,
            target_recipient,
            nonce,
            ctx
        );

        let message_ticket = transfer_tokens_with_payload<C>(
            token_bridge_state,
            transfer_ticket
        );

        publish_message::publish_message(
            wormhole_state,
            message_fee,
            message_ticket,
            the_clock
        );
    }


    public entry fun external_redeem_transfer_with_payload<C>(
        t_state: &State,
        wormhole_state: &WormholeState,
        token_bridge_state: &mut TokenBridgeState,
        raw_vaa: vector<u8>,
        the_clock: &Clock,
        ctx: &mut TxContext
    ) {
        let vaa = parse_and_verify(wormhole_state, raw_vaa, the_clock);
        let token_bridge_message = verify_only_once(token_bridge_state, vaa);
        let receipt = authorize_transfer<C>(token_bridge_state, token_bridge_message, ctx);

        redeem_transfer_with_payload(t_state, receipt, ctx)
    }
}