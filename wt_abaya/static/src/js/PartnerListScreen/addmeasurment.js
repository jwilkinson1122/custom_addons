/** @odoo-module */

import { PartnerListScreen } from "@point_of_sale/js/Screens/PartnerListScreen/PartnerListScreen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { MeasurmentPopup } from "@wt_abaya/js/Popups/MeasurmentPopup";

patch(PartnerListScreen.prototype, "wt_abaya.PartnerListScreen", {
	setup() {
		this._super();
		this.popup = useService("popup");
	},
	async Measurment(partner){
		 const { confirmed } =  await this.popup.add(MeasurmentPopup, {partner:partner});
	}

});
