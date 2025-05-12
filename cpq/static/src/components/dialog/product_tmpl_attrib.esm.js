/** @odoo-module */

import { onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { filterVisibleAttributeValues, getVisibleValueMap } from "./utils.esm";
const {Component} = owl;

class ProductTmplAttrib extends Component {

    setup() {
        super.setup(...arguments);
        this.user = useService("user");
        onWillStart(this.onWillStart);
    }

    async onWillStart() {
        console.log("Rendering", this.props.side, this.props.attribute.name, "with selected:", this.props.selected);
        console.log("Rendering attribute", this.props.attribute.name, "with selected:", this.props.selected);
    }

    stringify() {
        return JSON.stringify(this.props.attribute);
    }

    getPTAVTemplate() {
        switch (this.props.attribute.display_type) {
            case "color":
                return "cpq.ProductTmplAttrib-color";
            case "pills":
            case "radio":
            default:
                return "cpq.ProductTmplAttrib-radio";
        }
    }

    // getVisibleValues() {
    //     return filterVisibleAttributeValues(
    //         this.props.attribute,
    //         this.props.selected,
    //         this.props.allAttributes || []
    //     );
    // }

    // getVisibleValues() {
    //     const visible = filterVisibleAttributeValues(
    //         this.props.attribute,
    //         this.props.selected,
    //         this.props.allAttributes || []
    //     );
    //     console.log("🔎 Visible PTAVs for", this.props.attribute.name, "→", visible.map(v => v.name));
    //     return visible;
    // }

    getVisibleValues() {
        const valueMap = getVisibleValueMap(
            this.props.attribute,
            this.props.selected,
            this.props.allAttributes || []
        );
        console.log("🔎 Visible PTAVs for", this.props.attribute.name, "→", valueMap.map(v => v.name));
        return valueMap;
    }
    
    

    isSelectedPTAVCustom() {
        return false;   
    }

}

ProductTmplAttrib.template = "cpq.ProductTmplAttrib";

ProductTmplAttrib.props = {
    id: Number,
    attribute: {
        type: Object,
        shape: {
            id: Number,
            name: String,
            display_type: {
                type: String,
                validate: (type) =>
                    ["color", "pills", "radio", "select"].includes(type),
            },
            is_group: { type: Boolean, optional: true },     
            required: { type: Boolean, optional: true },     
            sequence: { type: Number, optional: true },       
            values: {
                type: Array,
                element: {
                    id: Number,
                    name: String,
                    html_color: [Boolean, String],
                    is_custom: Boolean,
                    price_extra: Number,
                    excluded: { type: Boolean, optional: true },
                    cpq_custom_type: [Boolean, String],
                    triggers: { type: Array, optional: true },
                    children: { type: Array, optional: true },
                },
            },
        },
    },
    selected: { type: Object, optional: true },
    side: { type: String, optional: true },
    hideLabel: { type: Boolean, optional: true },
    onSelect: { type: "function" },
    onCustom: { type: "function" },
};

export default ProductTmplAttrib;
