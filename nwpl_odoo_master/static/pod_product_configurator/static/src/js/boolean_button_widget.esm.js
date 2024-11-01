/** @odoo-module **/
import {registry} from "@web/core/registry";
import {onMounted, onRendered, useRef, useState} from "@odoo/owl";
import {BooleanField, booleanField} from "@web/views/fields/boolean/boolean_field";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
console.log(standardFieldProps)

export class BooleanButton extends BooleanField {
    //    Static template = "pod_product_configurator.BooleanButtonField";

    setup() {
        super.setup();
        this.state1 = useState({value: 0});
        this.root = useRef("root");
        onMounted(() => {
            this.updateConfigurableButton();
        });
        onRendered(() => {
            this.updateConfigurableButton();
        });
    }

    updateConfigurableButton() {
        this.text = this.props.value
            ? this.props.activeString
            : this.props.inactiveString;
        this.hover = this.props.value
            ? this.props.inactiveString
            : this.props.activeString;
        var val_color = this.props.value ? "text-success" : "text-danger";
        var hover_color = this.props.value ? "text-danger" : "text-success";
        var $val = $("<span>")
            .addClass("o_stat_text o_boolean_button o_not_hover " + val_color)
            .text(this.text);
        var $hover = $("<span>")
            .addClass("o_stat_text o_boolean_button o_hover d-none " + hover_color)
            .text(this.hover);
        $(this.root.el).empty();
        $(this.root.el).append($val).append($hover);
    }
}

export const BooleanButtonField = {
    ...booleanField,
    component: BooleanButton,
    extractProps: ({options}) => {
        return {
            activeString: options.active,
            inactiveString: options.inactive,
        };
    },
};

BooleanButton.props = {
    ...standardFieldProps,
    activeString: {type: String},
    inactiveString: {type: String, optional: true},
};

registry.category("fields").add("boolean_button", BooleanButtonField);


// export class BooleanButtonField extends BooleanField {
//     setup() {
//         super.setup();
//         this.state1 = useState({value: 0});
//         this.root = useRef("root");
//         console.log(this.props); 
//         onMounted(() => {
//             this.updateConfigurableButton();
//         });
//         onRendered(() => {
//             this.updateConfigurableButton();
//         });
//     }

//     onChange() {
//         this.state1.value++;
//     }

//     updateConfigurableButton() {
//         console.log(this.props); 
//         this.text = this.props.value
//             ? this.props.activeString || "Active"
//             : this.props.inactiveString || "Inactive";
//         this.hover = this.props.value
//             ? this.props.inactiveString || "Inactive"
//             : this.props.activeString || "Active";
        
//         var val_color = this.props.value ? "text-success" : "text-danger";
//         var hover_color = this.props.value ? "text-danger" : "text-success";
//         var $val = $("<span>")
//             .addClass("o_stat_text o_boolean_button o_not_hover " + val_color)
//             .text(this.text);
//         var $hover = $("<span>")
//             .addClass("o_stat_text o_boolean_button o_hover d-none " + hover_color)
//             .text(this.hover);
        
//         $(this.root.el).empty();
//         $(this.root.el).append($val).append($hover);
//     }
// }

// BooleanButtonField.props = {
//     ...standardFieldProps,
//     activeString: {type: String, optional: true},
//     inactiveString: {type: String, optional: true},
// };

// BooleanButtonField.extractProps = ({attrs}) => {
//     return {
//         activeString: attrs?.options?.active || 'Active',
//         inactiveString: attrs?.options?.inactive || 'Inactive',
//         name: attrs?.name || 'default_name', 
//     };
// };

// BooleanButtonField.template = "pod_product_configurator.BooleanButtonField";
// registry.category("fields").add("boolean_button", BooleanButtonField);

