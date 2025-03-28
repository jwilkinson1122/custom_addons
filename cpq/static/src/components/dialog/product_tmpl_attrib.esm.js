/** @odoo-module */

import { onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
const {Component} = owl;

class ProductTmplAttrib extends Component {

    setup() {
        super.setup(...arguments);
        this.user = useService("user");

        onWillStart(this.onWillStart);
    }

 

    // willStart() {
    //     console.log("🔄 Rendering attribute", this.props.attribute.name, "with selected:", this.props.selected);
    // }

    async onWillStart() {
        console.log("🔄 Rendering attribute", this.props.attribute.name, "with selected:", this.props.selected);
    }

    
    // --------------------------------------------------------------------------
    // Handlers
    // --------------------------------------------------------------------------
    //

    stringify() {
        return JSON.stringify(this.props.attribute);
    }

    // --------------------------------------------------------------------------
    // Private
    // --------------------------------------------------------------------------

    /**
     * Return template name to use by checking the display type in the props.
     *
     * Each attribute line can have one of this four display types:
     *      - 'Color'  : Display each attribute as a circle filled with said color.
     *      - 'Pills'  : Display each attribute as a rectangle-shaped element.
     *      - 'Radio'  : Display each attribute as a radio element.
     *      - 'Select' : Display each attribute in a selection tag.
     *
     * @returns {String} - The template name to use.
     */
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
    
    // getPTAVTemplate() {
    //     switch (this.props.attribute.display_type) {
    //         case "color":
    //             return "cpq.ProductTmplAttrib-color";
    //         case "pills":
    //         case "radio":
    //             return "cpq.ProductTmplAttrib-radio";
    //         case "select":
    //             return "cpq.ProductTmplAttrib-select";
    //     }
    // }

    // getPTAVTemplate() {
    //     return "cpq.ProductTmplAttrib-radio";
    // }

    isSelectedPTAVCustom() {
        return false;   
    }

    // isSelectedPTAVCustom() {
    //     return this.props.attribute.ptav_ids.some(
    //         (ptav) => ptav.is_custom && this.props.selected?.hasOwnProperty(ptav.id)
    //     );
    // }
    
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
            ptav_ids: {
                type: Array,
                element: {
                    type: Object,
                    shape: {
                        id: Number,
                        name: String,
                        html_color: [Boolean, String],
                        is_custom: Boolean,
                        price_extra: Number,
                        excluded: { type: Boolean, optional: true },
                        cpq_custom_type: [Boolean, String],
                        cpq_selection_values: {
                            optional: true,
                            type: Array,
                            element: { type: Array },
                        },
                    },
                },
            },
        },
    },
    selected: { type: Object, optional: true },
    hideLabel: { type: Boolean, optional: true },
    onSelect: { type: "function" },
    onCustom: { type: "function" },
};

export default ProductTmplAttrib;
