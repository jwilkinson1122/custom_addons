/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Orderline, Order } from "@point_of_sale/app/store/models";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { PosOrderCustomizationPopup } from "@nwpl_pod_master/static/pod_pos_order_customizations/app/pos_order_customization_popup/PosOrderCustomizationPopup";

patch(PosStore.prototype, {

    async _processData(loadedData) {
        await super._processData(...arguments);
        this._loadPosOrderCustomizationGroup(loadedData['pos.order.customization.group'])
        this._loadPosOrderCustomizations(loadedData['pos.order.customization'])
    },

    _loadPosOrderCustomizationGroup: function(customization_groups){
        var self = this;
        self.db.customization_group_by_id = {};
        customization_groups.forEach(element => {
            self.db.customization_group_by_id[element.id] = element;
        });
    },

    _loadPosOrderCustomizations: function(order_customizations){
        var self = this;
        self.db.customization_by_id = {};
        order_customizations.forEach(element => {
            self.db.customization_by_id[element.id] = element;
        });
    }
});

patch(Order.prototype, {

    add_product(product, options){
        var last_orderline = this.get_last_orderline();
        super.add_product(product, options);
        var updated_last_orderline = this.get_last_orderline();
        const popup = this.pos.env.services.popup;
        if (product.customization_group_ids && product.customization_group_ids.length && !(last_orderline && last_orderline.cid == updated_last_orderline.cid)){
            popup.add(PosOrderCustomizationPopup,{
                groups:product.customization_group_ids,
                product:product,
                line:updated_last_orderline,
            });
        }        
    }
    
});

patch(Orderline.prototype, {

    setup(_defaultObj, options){
        super.setup(...arguments);
        this.pod_customization_ids = this.pod_customization_ids || [];
        this.is_extra_price_set = this.is_extra_price_set || false;
        this.order_customizations = this.order_customizations || '';
        this.extra_price = 0;
    },

    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        if (json.pod_customization_ids){
            this.pod_customization_ids = json.pod_customization_ids
        }
        if (json.is_extra_price_set){
            this.is_extra_price_set = json.is_extra_price_set
        }
        if (json.extra_price) {
            this.extra_price = json.extra_price
        }
        if (json.order_customizations){
            this.order_customizations = json.order_customizations
        }
    },

    export_for_printing(){
        var dict = super.export_for_printing();
        dict.pod_customization_ids = this.pod_customization_ids;
        return dict;
    },

    export_as_JSON(){
        var json = super.export_as_JSON(...arguments);
        var current_order = this;
        json.full_product_name = this.get_full_product_name();
        if (current_order != null) {
            json.pod_customization_ids = current_order.pod_customization_ids;
            json.is_extra_price_set = current_order.is_extra_price_set;
            json.order_customizations = current_order.get_orderline_customizations();
        }
        if (this) {
            json.extra_price = this.extra_price;
        }
        return json;
    },
    

    get_orderline_customizations(){
        var self = this;
        var customization_text = '';
        if (self.pod_customization_ids){
            self.pod_customization_ids.forEach(function(customization_id){
                customization_text += self.pos.db.customization_by_id[customization_id].name + '\n';
            })
        }   
        return customization_text;
    },

    set_unit_price(price) {
        this.order.assert_editable();
        var self = this;
        var customization_ids = self.pod_customization_ids;
        if (customization_ids && customization_ids.length && !self.is_extra_price_set) {
            price -= self.extra_price;

            self.extra_price = 0;
            customization_ids.forEach(element => {
                self.extra_price += self.pos.db.customization_by_id[element].pos_extra_price;
            });
            self.is_extra_price_set = true;
            price += self.extra_price;
        } else {
            price -= self.extra_price;
            self.extra_price = 0;
        }
        super.set_unit_price(price);
    },

    getDisplayData() {
        var res = super.getDisplayData()
        res["orderline"] = this
        return res
    }

});

patch(ProductScreen.prototype, {
    _setValue(val) {
        var self = this;
        if (self.env && self.env.services.pos && self.env.services.pos.get_order()) {
            var order = self.env.services.pos.get_order();
            var order_line = order.get_selected_orderline()
            if (order_line) {
                if (self.env.services.pos.numpadMode === 'price' && val) {
                    order_line.pod_customization_ids = [];
                }
            }
        }
        super._setValue(val);
    }
});
