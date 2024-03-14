odoo.define('dv_pos_drugstore_popup.WhatsappScreen', function (require) {
    'use strict';

    const { is_email } = require('web.utils');
    const { useRef, useContext } = owl.hooks;
    const { useErrorHandlers, onChangeOrder } = require('point_of_sale.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');

    
    class WhatsappScreen extends AbstractReceiptScreen {
        constructor() {
            super(...arguments);
            useErrorHandlers();
            onChangeOrder(null, (newOrder) => newOrder && this.render());
            this.orderReceipt = useRef('order-receipt');
            const order = this.currentOrder;
            const client = order.get_client();
            this.orderUiState = useContext(order.uiState.ReceiptScreen);
            this.orderUiState.inputEmail = this.orderUiState.inputEmail || (client && client.email) || '';
            this.is_email = is_email;
        }
        mounted() {
            // Here, we send a task to the event loop that handles
            // the printing of the receipt when the component is mounted.
            // We are doing this because we want the receipt screen to be
            // displayed regardless of what happen to the handleAutoPrint
            // call.
            setTimeout(async () => {
                let images = this.orderReceipt.el.getElementsByTagName('img');
                for(let image of images) {
                    await image.decode();
                }
                await this.handleAutoPrint();
            }, 0);
        }
        async onSendMessage() {
            try {
                await this._sendReceiptToCustomerWTS();
                this.orderUiState.emailSuccessful = true;
                this.orderUiState.emailNotice = this.env._t('Email sent.');
            } catch (error) {
                
            }
        }
        async _sendReceiptToCustomerWTS() {
            const order = this.currentOrder;
            const orderName = order.get_name();
            const order_server_id = this.env.pos.validated_orders_name_server_id_map[orderName];
            await this.rpc({
                model: 'pos.order',
                method: 'action_receipt_to_customer_WTS',
                args: [[order_server_id]],
            });
        }
    }
    WhatsappScreen.template = 'WhatsappForm';
    return WhatsappScreen;
    
});
