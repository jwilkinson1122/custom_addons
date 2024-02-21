/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {ProductList} from "@sale_product_configurator/js/product_list/product_list";
import {jsonrpc} from "@web/core/network/rpc_service";


patch(ProductList.prototype, {
    async onkeyup(ev) {
        let xml_id = "sale_product_configurator_extended.product_attribute_" + ev.currentTarget.name;
        let current_value = parseInt(ev.currentTarget.value);
        if (current_value) {
            let product_id = parseInt($(ev.currentTarget).attr("product_id"));

            let result = await jsonrpc("/web/dataset/call_kw/website/write", {
                'model': 'product.template.attribute.value',
                'method': 'get_closest_value_for_product',
                'args': [xml_id, current_value, product_id],
                kwargs: {},
            });
            let attribute_id = result[0];
            let is_exact_match = result[1];
            $($($.find("option[value='" + attribute_id + "']")).parent()).val(attribute_id)
        }


    }
});
export default ProductList;
