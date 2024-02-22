/** @odoo-module **/

import {ProductTemplateAttributeLine} from "@sale_product_configurator/js/product_template_attribute_line/product_template_attribute_line";
import {jsonrpc} from "@web/core/network/rpc_service";
import {patch} from "@web/core/utils/patch";


patch(ProductTemplateAttributeLine.prototype, {
    props: {
        productTmplId: Number,
        id: Number,
        attribute: {
            type: Object,
            shape: {
                id: Number,
                name: String,
                display_type: {
                    type: String,
                    validate: type => ["color", "multi", "pills", "radio", "select", "dimension"].includes(type),
                },
            },
        },
        attribute_values: {
            type: Array,
            element: {
                type: Object,
                shape: {
                    id: Number,
                    name: String,
                    html_color: [Boolean, String], // backend sends 'false' when there is no color
                    image: [Boolean, String], // backend sends 'false' when there is no image set
                    is_custom: Boolean,
                    price_extra: Number,
                    excluded: { type: Boolean, optional: true },
                },
            },
        },
        selected_attribute_value_ids: { type: Array, element: Number },
        create_variant: {
            type: String,
            validate: type => ["always", "dynamic", "no_variant"].includes(type),
        },
        customValue: { type: String, optional: true },
    },
    getPTAVTemplate() {
        switch(this.props.attribute.display_type) {
            case 'color':
                return 'saleProductConfigurator.ptav-color';
            case 'multi':
                return 'saleProductConfigurator.ptav-multi';
            case 'pills':
                return 'saleProductConfigurator.ptav-pills';
            case 'radio':
                return 'saleProductConfigurator.ptav-radio';
            case 'select':
                return 'saleProductConfigurator.ptav-select';
            case 'dimension':
                return 'saleProductConfigurator.ptav-dimension';
        }
    }
});
export default ProductTemplateAttributeLine;
