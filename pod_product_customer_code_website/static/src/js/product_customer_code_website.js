/** @odoo-module **/

import { WebsiteSale } from '@website_sale/js/website_sale';
import '@website_sale/js/website_sale';

WebsiteSale.include({
    /**
     * Adds the stock checking to the regular _onChangeCombination method
     * @override
    */
    _onChangeCombination: function (ev, $parent, combination) {
        this._super.apply(this, arguments);            
        if (combination.product_name || combination.product_name) {
            var html_table = '<table class="table"><thead><tr><th>Product Customer Code</th><th>Product Customer Name</th></tr></thead><tbody><tr>'
            html_table +=  '<td>'+combination.customer_code+'</td>'
            html_table +=  '<td>'+combination.product_name+'</td>'
            html_table += '</tr></tbody></table>'  
            $('.js_cls_dynamic_product_customer_table').html(html_table)
        }
        else{
            $('.js_cls_dynamic_product_customer_table').html('')
        }
    }
});
