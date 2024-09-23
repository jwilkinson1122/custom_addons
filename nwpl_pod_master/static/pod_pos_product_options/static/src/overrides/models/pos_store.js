/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OptionsPopup } from "@nwpl_pod_master/static/pod_pos_product_options/app/Popups/OptionsPopup/OptionsPopup";

patch(PosStore.prototype, {
    //@override
    async addProductToCurrentOrder(product, options = {}) {
        console.log("Adding product to current order: ", product);
        var self = this;
        await super.addProductToCurrentOrder(product, options = {})
        var category;
        var product_ids = []
        var Option_products = []

        if (product.pos_categ_id && product.pos_categ_id[0]) {
            category = self.db.get_category_by_id(product.pos_categ_id[0])
        }

        if (category && category.pod_product_option_ids) {
            category.pod_product_option_ids.forEach(function (product_id) {
                if(self.db.product_by_id[product_id]){
                    Option_products.push(self.db.product_by_id[product_id])
                    product_ids.push(product_id)
                }
            });
        }

        await product.pod_option_ids.forEach(function (each_id) {
            if (!product_ids.includes(each_id)) {
                if(self.db.product_by_id[each_id]){
                    Option_products.push(self.db.product_by_id[each_id])
                }
            }
        });

        if (self.config.pod_add_options_on_click_product && self.config.pod_enable_options) {
            if (Option_products.length > 0) {
                let { confirmed } = await this.popup.add(OptionsPopup, {'title' : 'Options','Option_products': Option_products, 'Globaloptions': []});
                if (confirmed) {
                    // Continue to add product to order without showing MeasurementPopup
                } else {
                    return;
                }
            }
        }
    }
});

// patch(PosStore.prototype, {
//     async addProductToCurrentOrder(product, options = {}) {
//         try {
//             var self = this;
//             await super.addProductToCurrentOrder(product, options);
//             var category;
//             var product_ids = [];
//             var Option_products = [];

//             if (product.pos_categ_id && product.pos_categ_id[0]) {
//                 category = self.db.get_category_by_id(product.pos_categ_id[0]);
//             }

//             if (category && category.pod_product_option_ids) {
//                 category.pod_product_option_ids.forEach(function(product_id) {
//                     if (self.db.product_by_id[product_id]) {
//                         Option_products.push(self.db.product_by_id[product_id]);
//                         product_ids.push(product_id);
//                     }
//                 });
//             }

//             await product.pod_option_ids.forEach(function(each_id) {
//                 if (!product_ids.includes(each_id)) {
//                     if (self.db.product_by_id[each_id]) {
//                         Option_products.push(self.db.product_by_id[each_id]);
//                     }
//                 }
//             });

//             var allproducts = [];
//             var searchBox = $('.search-box input');

//             if (!self.isMobile && searchBox.length && searchBox.val() !== "") {
//                 var searchInput = searchBox.val();
//                 if (searchInput) {
//                     allproducts = this.db.search_product_in_category(self.selectedCategoryId, searchInput);
//                 } else {
//                     console.error("Search input is undefined or empty");
//                 }
//             } else {
//                 allproducts = self.db.get_product_by_category(0);
//             }

//             if (self.config.pod_add_options_on_click_product && self.config.pod_enable_options) {
//                 if (Option_products.length > 0) {
//                     let { confirmed } = await this.popup.add(OptionsPopup, { 'title': 'Options', 'Option_products': Option_products, 'Globaloptions': [] });
//                     if (confirmed) {
//                     } else {
//                         return;
//                     }
//                 }
//             }
//         } catch (error) {
//             console.error("Error in addProductToCurrentOrder: ", error);
//         }
//     }
// });

 