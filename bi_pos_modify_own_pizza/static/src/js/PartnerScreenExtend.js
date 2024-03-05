/** @odoo-module */

import { PartnerListScreen } from "@point_of_sale/app/screens/partner_list/partner_list";
import { patch } from "@web/core/utils/patch";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";

patch(PartnerListScreen.prototype, {
    async clickPartner(partner) {

        var orderlines = this.pos.get_order() ? this.pos.get_order().get_orderlines() : [];
        const{Confirmed} = false;
        if(this.pos.config.product_configure && orderlines.length > 0){
            for (var line in orderlines)
            {
                if(orderlines[line] && orderlines[line].product && orderlines[line].product.pizza_pieces){
                    const { confirmed } = await this.pos.popup.add(ConfirmPopup, {
                        title: _t('Warning'),
                        body: _t('If you change customer then the price of the combo product will be changed.'),
                    });
                    if(confirmed){
                    	if (this.state.selectedPartner && this.state.selectedPartner.id === partner.id) {
			                this.state.selectedPartner = null;
			            } else {
			                this.state.selectedPartner = partner;
			            }
			            this.confirm();
			            
		            }
			        else{
			        	this.pos.closeTempScreen();
			        	return
			        }

                }
            }
            
        }
       	if (this.state.selectedPartner && this.state.selectedPartner.id === partner.id) {
            this.state.selectedPartner = null;
        } else {
            this.state.selectedPartner = partner;
        }
        this.confirm();
    }
});
