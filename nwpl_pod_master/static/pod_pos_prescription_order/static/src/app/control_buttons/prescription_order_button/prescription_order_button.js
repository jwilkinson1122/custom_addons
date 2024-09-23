/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { PrescriptionOrderPopup } from "@nwpl_pod_master/static/pod_prescription_order/app/popups/prescription_order_popup/prescription_order_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";


export class PrescriptionOrderButton extends Component {
    static template = "pod_prescription_order.PrescriptionOrderButton";
    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async onClick() {
    // by clicking the prescription order button, it will check whether at least one product and the selected customer or not, after that it will display popup.
        var order=this.pos.selectedOrder
        var order_lines = order.orderlines;
        var partner = order.partner
        if (partner == null) {
            this.pos.popup.add(ErrorPopup, {
                    title: _t("Please Select the Customer"),
                    body: _t(
                        "You need to select a customer for using this option"
                    ),
                });
        } else if (order_lines.length == 0) {
            this.pos.popup.add(ErrorPopup, {
                    title: _t("Order line is empty"),
                    body: _t(
                        "Please select at least one product"
                    ),
                });
        } else {
          await this.pos.popup.add(PrescriptionOrderPopup, {
            title: _t("Prescription Order"),
            partner:partner,
            order:order,
              currentDate: new Date().toISOString().split('T')[0],
        });
        }
    }
}

ProductScreen.addControlButton({
    component: PrescriptionOrderButton,
    condition: function () {
        return this.pos.config.enable_prescriptions;
    },
});
