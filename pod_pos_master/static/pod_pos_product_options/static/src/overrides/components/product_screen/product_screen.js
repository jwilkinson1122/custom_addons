/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { OptionsPopup } from "@pod_pos_master/static/pod_pos_product_options/app/Popups/OptionsPopup/OptionsPopup";
import { useService } from "@web/core/utils/hooks";

patch(ProductScreen.prototype, {
    async selectLine(orderline) {
        await super.selectLine(orderline)
        var self = this;
            const product = orderline.get_product()
            var category;
            var product_ids = []
            var Option_products = []

            if (product.pos_categ_id && product.pos_categ_id[0]) {
                category = self.pos.db.get_category_by_id(product.pos_categ_id[0])
            }

            if (category && category.pod_product_option_ids) {
                category.pod_product_option_ids.forEach(function (product_id) {
                    if(self.pos.db.product_by_id[product_id]){
                        Option_products.push(self.pos.db.product_by_id[product_id])
                        product_ids.push(product_id)
                    }
                });
            }
            await product.pod_option_ids.forEach(function (each_id) {
                if (!product_ids.includes(each_id)) {
                    if(self.pos.db.product_by_id[each_id]){
                        Option_products.push(self.pos.db.product_by_id[each_id])
                    }
                }
            });

            var allproducts = []
            if (!self.isMobile && $('.search-box input') && $('.search-box input').val() != "") {
                allproducts = this.pos.db.search_product_in_category(
                    self.pos.selectedCategoryId,
                    $('.search-box input').val()
                );
            } else {
                allproducts = self.pos.db.get_product_by_category(0);
            }


            if (self.pos.config.pod_enable_options) {
                if (Option_products.length > 0) {
                    let { confirmed } = await  this.popup.add(OptionsPopup, {'title' : 'Options','Option_products': Option_products, 'Globaloptions': []});
                    if (confirmed) {
                    } else {
                        return;
                    }
                }
            }
    },
    setup() {
        super.setup()
        this.popup = useService("popup");
    },
    async _clickRemoveLine({ detail: line_id }) {
        var self = this;
        
        setTimeout(async () => {
            var order = self.env.pos.get_order()
            var line = this.env.pos.get_order().get_orderline(line_id)
            if (order && order.get_selected_orderline() && order.get_selected_orderline().Options) {

                var data = await $.grep(order.get_selected_orderline().Options, function (option) {
                    return option.id != line_id;
                });

                var data1 = await $.grep(order.get_selected_orderline().Options_temp, function (option1) {
                    return option1.id != line_id;
                });

                order.get_selected_orderline().Options = data
                order.get_selected_orderline().Options_temp = data1

                self.pos.get_order().removeOrderline(line)
            }
        }, 100);
    },
});
