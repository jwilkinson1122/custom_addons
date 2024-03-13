/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    /**
     * @override
     */

    setup() {super.setup();}, 

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
                    
                    var DeviceRadio = document.querySelector(
                        'input[type=radio][name=x]:checked'
                    );
                    if (DeviceRadio){
                        DeviceRadio.checked = false;
                        $('.modifiers-product-list').hide();
                        $('#bilateral_device').hide();
                        $('#left_device').hide();
                        $('#right_device').hide();
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
    },

    get selectedOrderlineQuantity() {
        const order = this.pos.get_order();
        const orderline = order.get_selected_orderline();
        if (this.pos.config.module_pos_manufacturing && this.pos.orderPreparationCategories.size) {
            let orderline_name = orderline.product.display_name;
            if (orderline.description) {
                orderline_name += " (" + orderline.description + ")";
            }
            const changes = Object.values(order.getOrderChanges().orderlines).find(
                (change) => change.name == orderline_name
            );
            return changes ? changes.quantity : false;
        }
        return super.selectedOrderlineQuantity;
    },

    get selectedOrderlineTotal() {
        return this.env.utils.formatCurrency(
            this.pos.get_order().get_selected_orderline().get_display_price()
        );
    },

    get nbrOfChanges() {
        return this.currentOrder.getOrderChanges().nbrOfChanges;
    },

    get swapButton() {
        return this.pos.config.module_pos_manufacturing && this.pos.orderPreparationCategories.size;
    },

    submitOrder() {
        this.pos.sendOrderInPreparation(this.pos.get_order());
    },

    get primaryReviewButton() {
        return (
            !this.primaryOrderButton &&
            !this.pos.get_order().is_empty() &&
            this.pos.config.module_pos_manufacturing
        );
    },

    get primaryOrderButton() {
        return (
            this.pos.get_order().getOrderChanges().nbrOfChanges !== 0 &&
            this.pos.config.module_pos_manufacturing
        );
    },

});
