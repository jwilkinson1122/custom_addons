/** @odoo-module */

import { CategorySelector } from "@point_of_sale/app/generic_components/category_selector/category_selector";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(CategorySelector.prototype, {
    setup(){
        super.setup();
        this.ui = useState(useService("ui"));
    },
    onClickProductGridView(){
        $('.product_grid_view').addClass('highlight')
        $('.product-list-container').removeClass('hide_product_list_container')

        $('.product_list_view').removeClass('highlight')
        $('.pod_product_list_view').addClass('hide_pod_product_list_view')
    },
    onClickProductListView(){
        $('.product_grid_view').removeClass('highlight')
        $('.product-list-container').addClass('hide_product_list_container')

        $('.product_list_view').addClass('highlight')
        $('.pod_product_list_view').removeClass('hide_pod_product_list_view')
    },
    isMobile() {
        return this.ui.isSmall
    }
});
