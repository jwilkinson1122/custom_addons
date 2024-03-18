/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
// import { ReceiptScreen } from "@point_of_sale/../tests/tours/helpers/ReceiptScreenTourMethods";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { formatFloat, formatMonetary } from "@web/views/fields/formatters";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

export class OptionsPopup extends AbstractAwaitablePopup {
    static template = "pod_pos_product_options.OptionsPopup";
    setup() {
        super.setup();
        this.pos = usePos();
        this.numberBuffer = useService("number_buffer");
          this.popup = useService("popup");
        // useListener('click-option-product', this._clickoptionProduct);
    }
    ClickOk(){ 
        this.props.resolve({ confirmed: true, payload: null });
        this.cancel();
    }
    get globalOptions(){
        return this.props.Globaloptions
    }
    get optionProducts(){
        return this.props.Option_products
    }
    get imageUrl() {
        const product = this.product; 
        return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
    }
    get pricelist() {
        const current_order = this.pos.get_order();
        if (current_order) {
            return current_order.pricelist;
        }
        return this.pos.default_pricelist;
    }
    get price() {
        const { currencyId, digits } = this.env;
        const formattedUnitPrice = formatMonetary(this.product.get_price(this.pricelist, 1), { currencyId, digits });

        if (this.product.to_weight) {
            return `${formattedUnitPrice}/${
                this.pos.units_by_id[this.product.uom_id[0]].name
            }`;
        } else {
            return formattedUnitPrice;
        }
    }
    async _clickoptionProduct(event){
        if (!this.pos.get_order()) {
            this.pos.add_new_order();
        }
        const product = event;
        if (this.pos.config.pod_enable_options && this.pos.get_order() && this.pos.get_order().get_selected_orderline()){
            this.pos.get_order().add_option_product(product);
        }else{
            await this.popup.add(ErrorPopup, {
                title: 'Please Select Orderline !',
            });
            // await  this.popup.add(ErrorPopup, {title : 'Please Select Orderline !',body: '123'});
                
            // this.showPopup('ErrorPopup', { 
            //     title: 'Please Select Orderline !'
            // })
        }
        this.numberBuffer.reset();
    }
}
  