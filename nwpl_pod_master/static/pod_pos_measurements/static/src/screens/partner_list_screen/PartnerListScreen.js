/** @odoo-module */

import { PartnerListScreen } from "@point_of_sale/app/screens/partner_list/partner_list";
import { MeasurementPopup } from "@nwpl_pod_master/static/pod_pos_measurements/app/popups/measurement_popup/MeasurementPopup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { onMounted } from "@odoo/owl";

patch(PartnerListScreen.prototype, {

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.popup = useService("popup");
        this.pos = usePos();
 
        if (typeof this.Measurement !== "function") {
            console.warn("Measurement method not found in PartnerListScreen.");
        }

    },
 
    async Measurement(partner) {
        const categories = this.pos.db.category_by_id;
        const measurement_types_by_id = this.pos.db.measurement_types_by_id;
        
        const filteredCategories = Object.values(categories).filter(category => {
            const measurement_type_ids = category.measurement_type_ids;
            if (Array.isArray(measurement_type_ids) && measurement_type_ids.length > 0) {
                return measurement_type_ids.some(id => measurement_types_by_id.hasOwnProperty(id));
            }
            return false;
        });

        if (filteredCategories.length === 0) {
            this.popup.add(ErrorPopup, {
                title: "No Meaurement Types",
                body: "No categories have measurement types assigned. Please assign measurement types to categories first.",
                confirmText: "Ok",
                onConfirm: () => {
                    this.popup.close();
                },
            });
        } else {
            const { confirmed } = await this.popup.add(MeasurementPopup, { partner });
            if (confirmed) {
                console.log("Measurement confirmed for partner:", partner);
            }
        }
    },

});


