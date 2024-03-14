/** @odoo-module */

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { Product } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { Component, onMounted, useExternalListener, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(ProductsWidget.prototype, {
	setup() {
        super.setup();
        this.pos = usePos();
    },

    get productsToDisplay() {
    	let self = this;
        let prods = super.productsToDisplay;

        let new_prods = [];
		let config_shop = self.pos.config.shop_id;
		if(config_shop){
			config_shop = config_shop[0];
			$.each(prods, function( i, prd ){
				if(prd.shop_ids){
					let is_valid = prd.shop_ids.indexOf(config_shop);
					if(is_valid >= 0){new_prods.push(prd);}
				}
			});
			return new_prods;
		}
		else{
			return prods;
		}
    }
});