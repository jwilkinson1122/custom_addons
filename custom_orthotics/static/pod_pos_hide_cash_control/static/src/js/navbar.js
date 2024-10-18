/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { useState } from "@odoo/owl";
import { ConnectionLostError, ConnectionAbortedError } from "@web/core/network/rpc_service";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";
import {
    formatFloat,
    roundDecimals as round_di,
    roundPrecision as round_pr,
    floatIsZero,
} from "@web/core/utils/numbers";


patch(Navbar.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
    },


    round_decimals_currency(value) {
        const decimals = this.pos.currency.decimal_places;
        return parseFloat(round_di(value, decimals).toFixed(decimals));
    },

    async getClosePosInfo() {
        const closingData =  await this.orm.call("pos.session", "get_closing_control_data", [
            [this.pos.pos_session.id],
        ]);
        const ordersDetails = closingData.orders_details;
        const paymentsAmount = closingData.payments_amount;
        const payLaterAmount = closingData.pay_later_amount;
        const openingNotes = closingData.opening_notes;
        const defaultCashDetails = closingData.default_cash_details;
        const otherPaymentMethods = closingData.other_payment_methods;
        const isManager = closingData.is_manager;
        const amountAuthorizedDiff = closingData.amount_authorized_diff;
        const cashControl = this.pos.config.cash_control;

        // component state and refs definition
        const state = {notes: '', acceptClosing: false, payments: {}};
        if (cashControl) {
            state.payments[defaultCashDetails.id] = {counted: 0, difference: -defaultCashDetails.amount, number: 0};
        }

        if (otherPaymentMethods.length > 0) {
            otherPaymentMethods.forEach(pm => {
                if (pm.type === 'bank') {
                    state.payments[pm.id] = {counted: this.round_decimals_currency(pm.amount), difference: 0, number: pm.number}
                }
            })
        }

        return {
            ordersDetails, paymentsAmount, payLaterAmount, openingNotes, defaultCashDetails, otherPaymentMethods,
            isManager, amountAuthorizedDiff, state, cashControl
        }
    },

    async getInitialState() {
        const info = await this.getClosePosInfo();
        const initialState = { notes: "", payments: {} };
        if (this.pos.config.cash_control) {
            initialState.payments[info.default_cash_details.id] = {
                counted: "0",
            };
        }
        info.other_payment_methods.forEach((pm) => {
            if (pm.type === "bank") {
                initialState.payments[pm.id] = {
                    counted: this.env.utils.formatCurrency(pm.amount, false),
                };
            }
        });
        return initialState;
    },

    async closeSession() {
        const info = await this.getClosePosInfo();
        if(this.pos.config.pod_enable_cash_control){
            const info = await this.pos.getClosePosInfo();
            this.popup.add(ClosePosPopup, { ...info, keepBehind: true }); 
        }
        else{
            this.customerDisplay?.update({ closeUI: true });
            this.pos.config.cash_control = true
            let cash_count;
            if (info.defaultCashDetails){
                cash_count = info.defaultCashDetails.payment_amount + info.defaultCashDetails.opening
            }
            if (this.pos.config.cash_control  && cash_count) {
                const response = await this.orm.call(
                    "pos.session",
                    "post_closing_cash_details",
                    [this.pos.pos_session.id],
                    {
                        counted_cash: parseFloat(
                            cash_count
                        ),
                    }
                );
                if (!response.successful) {
                    return this.handleClosingError(response);
                }
            }

            await this.orm.call("pos.session", "update_closing_control_state_session", [
                this.pos.pos_session.id,
                info.state.notes,
            ]);
                
            try {
                const bankPaymentMethodDiffPairs = info.otherPaymentMethods
                    .filter((pm) => pm.type == "bank")
                    .map((pm) => [pm.id, info.state.payments[pm.id].difference]);
                const response = await this.orm.call("pos.session", "close_session_from_ui", [
                    this.pos.pos_session.id,
                    bankPaymentMethodDiffPairs,
                ]);
                if (!response.successful) {
                    return this.handleClosingError(response);
                }
                window.location = "/web#action=point_of_sale.action_client_pos_menu";
                
            } catch (error) {
                if (error instanceof ConnectionLostError) {
                    throw error;
                } else {
                    await this.popup.add(ErrorPopup, {
                        title: _t("Closing session error"),
                        body: _t(
                            "An error has occurred when trying to close the session.\n" +
                                "You will be redirected to the back-end to manually close the session."
                        ),
                    });
                    window.location = "/web#action=point_of_sale.action_client_pos_menu";
                }
            }
        }
    },

    async handleClosingError(response) {
        await this.popup.add(ErrorPopup, {
            title: response.title || "Error",
            body: response.message,
            sound: response.type !== "alert",
        });
        if (response.redirect) {
            window.location = "/web#action=point_of_sale.action_client_pos_menu";
        }
    }

});
