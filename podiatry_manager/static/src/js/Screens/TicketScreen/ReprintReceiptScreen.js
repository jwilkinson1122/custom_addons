odoo.define('podiatry_manager.ReprintReceiptScreen', function (require) {
    'use strict';

    const AbstractReceiptScreen = require('podiatry_manager.AbstractReceiptScreen');
    const Registries = require('podiatry_manager.Registries');

    const ReprintReceiptScreen = (AbstractReceiptScreen) => {
        class ReprintReceiptScreen extends AbstractReceiptScreen {
            mounted() {
                this.printReceipt();
            }
            confirm() {
                this.showScreen('TicketScreen', { reuseSavedUIState: true });
            }
            async printReceipt() {
                if(this.env.pos.proxy.printer && this.env.pos.config.iface_print_skip_screen) {
                    let result = await this._printReceipt();
                    if(result)
                        this.showScreen('TicketScreen', { reuseSavedUIState: true });
                }
            }
            async tryReprint() {
                await this._printReceipt();
            }
        }
        ReprintReceiptScreen.template = 'ReprintReceiptScreen';
        return ReprintReceiptScreen;
    };
    Registries.Component.addByExtending(ReprintReceiptScreen, AbstractReceiptScreen);

    return ReprintReceiptScreen;
});
