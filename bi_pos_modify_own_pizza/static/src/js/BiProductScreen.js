/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

patch(ProductScreen.prototype, {
   setup() {
		super.setup();
	}, 
    _setValue(val) {
        if (this.currentOrder.get_selected_orderline()) {
            if (this.pos.numpadMode === 'quantity') {

            	if (val === "remove") {
                    this.currentOrder.removeOrderline(this.currentOrder.get_selected_orderline());
                } else {
                    const result = this.currentOrder.get_selected_orderline().set_quantity(val);
                    if (!result) {
                        this.numberBuffer.reset();
                    }
                }
                // const result = this.currentOrder.get_selected_orderline().set_quantity(val);

                if (val== 'remove'){
                    $('.modifiers-list').hide();
        			
        			$('.products-widget-control').removeClass('d-none');
            		$('.product-list').removeClass('d-none');
                    $('.product-list').show();
                    $('.products-widget-control').show();
                    self.modifier_attribute = [];
                    
                    var PizzaRadio = document.querySelector(
                        'input[type=radio][name=x]:checked'
                    );
                    if (PizzaRadio){
                        PizzaRadio.checked = false;
                        $('.modifiers-product-list').hide();
                        $('#full_pizza').hide();
                        $('#half_pizza').hide();
                        $('#quater_pizza').hide();
                        $('#ask').show();
                    }
                }
            } else if (this.pos.numpadMode === 'discount') {
                this.currentOrder.get_selected_orderline().set_discount(val);
            } else if (this.pos.numpadMode === 'price') {
                var selected_orderline = this.currentOrder.get_selected_orderline();
                selected_orderline.price_manually_set = true;
                selected_orderline.set_unit_price(val);
            }
        }
    }
});

