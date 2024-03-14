/** @odoo-module */

import { Chrome } from "@point_of_sale/app/pos_app";
import { patch } from "@web/core/utils/patch";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { CashOpeningPopup } from "@point_of_sale/app/store/cash_opening_popup/cash_opening_popup";


patch(PosStore.prototype, {

    async setup() {
        await super.setup(...arguments);
    },
    shouldShowCashControl() {
        return this.config.cash_control && this.pos_session.state == "opening_control";
    },
    openCashControl() {
        if (this.shouldShowCashControl()) {
            if(this.config.cash_control){
                this.popup.add(CashOpeningPopup, { keepBehind: true });
            }
            else{
                this.pos_session.cash_register_balance_start = this.config.last_session_closing_cash;
                this.pos_session.state = 'opened';
                this.orm.call(
                       'pos.session',
                       'set_cashbox_pos',
                        [this.pos_session.id, this.config.last_session_closing_cash,this.states.notes]
                );
            }
        }
    }
});






