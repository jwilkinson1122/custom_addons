/** @odoo-module */

import { ConfirmPopup } from "@point_of_sale/js/Popups/ConfirmPopup";
import { AbstractAwaitablePopup } from "@point_of_sale/js/Popups/AbstractAwaitablePopup";
import { _lt } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/pos_hook";
import { renderToElement } from "@web/core/utils/render";
import { useService } from "@web/core/utils/hooks";
import { PosDB } from "@point_of_sale/js/db";
import { ErrorPopup } from "@point_of_sale/js/Popups/ErrorPopup";

export class SetMeasurmentPopupWidget extends ConfirmPopup {
	static template = "SetMeasurmentPopupWidget";
	static defaultProps = { confirmKey: false };
	setup() {
		super.setup();
		this.rpc = useService('rpc');
		this.orm = useService("orm");
		this.db = new PosDB()
		this.pos = usePos();
		Object.assign(this, this.props.info);
	}

	async confirm() {
		const measurment_category = $('.js_measurment_set').find('input:checked')
		if(measurment_category && measurment_category.val()){
			if (measurment_category[0].name === "measurment_category"){
				var measurment_cat = this.pos.globalState.db.get_measurment_category_by_id(parseInt(measurment_category.val()))
				var measurment = this.pos.globalState.db.get_measurment_by_id(measurment_cat.measurment_ids)
				var selected_orderline = this.pos.globalState.get_order().get_selected_orderline()
				selected_orderline.set_measurment_ids(measurment)
				selected_orderline.set_measurment_unit(measurment_cat.measurment_unit)
			}
		}
		this.cancel()
	}
}