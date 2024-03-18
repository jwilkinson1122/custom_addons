/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { ProductStockRestrict } from "@pod_pos_master/static/pod_pos_wh_stock/app/popups/restrict_sale_popup/restrict_sale_popup";
import { _t } from "@web/core/l10n/translation";
import { VariantPopup } from "@pod_pos_master/static/pod_pos_product_variant/app/popups/variant_popup/variant_popup"


patch(PosStore.prototype, {

    push_single_order(order) {
        var self = this;
        const result = super.push_single_order(order)
        var date = new Date()
        // formate roday date
        var date_str =  date.getFullYear() +'-'+  date.getMonth() +'-'+ date.getDate() +'- '+ date.getHours()+':'+ date.getMinutes()+ ':'+ date.getSeconds();
        if (result){
            var order_line_list = []
            for (let line of order.get_orderlines()){
                order_line_list.push(line.export_as_JSON())
            }
            result.then(function (Orders) {
                if ( Orders ){
                    let order_id = Orders[0].id
                    // set name
                    order.pod_created_seq = Orders[0].name
                    // Pushed ordeer to order list
                    
                    self.db.pos_order_by_id[order_id] = [{
                        'id': order_id, 
                        'name': Orders[0].name  , 
                        'date_order':  date_str, 
                        'partner_id':  order.get_partner() ? order.get_partner().id : false , 
                        'partner_name':  order.get_partner() ? order.get_partner().name : false , 
                        'pos_reference': order.name, 
                        'amount_total': order.get_total_with_tax() , 
                        'state': Orders[0].account_move ? 'invoiced' : 'paid', 
                    }, order_line_list]
                }
            })
        }
        return result
    },
    async addProductToCurrentOrder(product, options = {}) {
        var order = this.get_order()
        var self = this;
        if (this.config.pod_show_qty_location && this.config.pod_display_stock && product.type == "product") {
            var pod_min_qty = this.config.pod_min_qty
            var location_id = this.config.pod_pos_location ? this.config.pod_pos_location[0] : false

            var stocks = this.db.get_stock_by_product_id(product.id)
            var stock_qty = 0.00
            if (location_id && stocks && stocks.length) {
                var pod_stock = stocks.filter((stock) => stock.location_id == location_id)
                if (pod_stock && pod_stock.length) {
                    stock_qty = pod_stock[0].quantity
                }
            }
            var line = order.get_orderlines().filter((x) => x.product.id == product.id)
            if (line && line.length) {
                let restrict_popup = false
                let qty = 0.00
                for (let ol of line) {
                    qty += ol.quantity
                    if (ol && ol.product.id == product.id && (stock_qty - qty) <= pod_min_qty_min_qty) {
                        restrict_popup = true
                    }
                }
                if (restrict_popup) {
                    const { confirmed, payload } = await this.env.services.popup.add(ProductStockRestrict, {
                        title: _t(product.display_name),
                        body: _t('Minimum availabe quantity is ' + pod_min_qty),
                        'product': product,
                    });

                    if (confirmed) {
                        await super.addProductToCurrentOrder(...arguments)
                    }
                } else {
                    await super.addProductToCurrentOrder(...arguments)
                }
            } else {
                if ((stock_qty - 1) <= pod_min_qty) {
                    const { confirmed, payload } = await this.env.services.popup.add(ProductStockRestrict, {
                        title: _t(product.display_name),
                        body: _t('Minimum availabe quantity is ' + pod_min_qty),
                        'product': product,
                    });
                    if (confirmed) {
                        await super.addProductToCurrentOrder(...arguments)
                    }
                } else {
                    await super.addProductToCurrentOrder(...arguments)
                }
            }
        } else {
            await super.addProductToCurrentOrder(...arguments)
        }

        if( self.config.pod_pos_enable_product_variants && self.config.pod_pos_display_alternative_products ){
            var alternative_products = []
            if(product.pod_alternative_products && product.pod_alternative_products.length){
                for (let sub_pro_id of product.pod_alternative_products){
                    var sub_pro = self.db.product_by_id[sub_pro_id]    
                    alternative_products.push(sub_pro)
                }
                await this.popup.add(VariantPopup, {
                    title: _t("Product Variants"),
                    product_variants: [],
                    'alternative_products': alternative_products
                });
            }
        }

    }
});