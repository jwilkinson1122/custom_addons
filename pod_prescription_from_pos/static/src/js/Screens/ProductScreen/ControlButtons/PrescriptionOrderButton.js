/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

export class PrescriptionOrderButton extends Component {
	static template = "pod_prescription_from_pos.PrescriptionOrderButton";
	setup() {
		this.pos = usePos();
		this.orm = useService("orm");
		this.popup = useService("popup");
	}
	async onClick() {
		var self = this;
		const oderdetails = {};
		let selectedOrder = self.pos.get_order();
		if (selectedOrder.get_partner()){
			if (this.pos.get_order().get_orderlines().length > 0){
				this.pos.get_order().get_orderlines().forEach(function(orderLine) {
					oderdetails[orderLine.id] = { 
						product: orderLine.get_product().id, 
						quantity: orderLine.quantity,
						price: orderLine.price,
						discount: orderLine.discount,
						};
				});
				if (this.pos.get_order().get_total_tax() > 0){
					oderdetails['tax_amount'] = this.pos.get_order().get_total_tax()
				}
				oderdetails['partner_id'] = selectedOrder.get_partner().id;
				const result = await this.orm.call('prescription.order','create_prescription_from_pos', [oderdetails]);
				if(result){
					this.pos.showScreen('ProductScreen');
					await this.popup.add(ConfirmPopup, {
						title: this.env._t('Successfully!'),
						body: this.env._t(
							'Prescriptions Order ' + result.name +' Created Successfully!!!!'
						),
					});
				}

			}
			else if(this.pos.get_order().get_orderlines().length <= 0){
				await this.popup.add(ErrorPopup, {
					title: this.env._t('No Product'),
					body: this.env._t("There are no Product for PrescriptionOrder."),
				});
			}
		}
		else{
			await this.popup.add(ErrorPopup, {
				title: this.env._t('Unknown Customer'),
				body: this.env._t("Select Customer."),
			});
		}
	}
}

ProductScreen.addControlButton({
	component: PrescriptionOrderButton,
	condition: function () {
        return this.pos.config.create_rx;
    },
});
