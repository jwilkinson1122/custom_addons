/** @odoo-module */

import { TModelInput } from "@pod_point_of_sale/app/generic_components/inputs/t_model_input";

export class NumericInput extends TModelInput {
    static template = "pod_point_of_sale.NumericInput";
    static props = {
        ...super.props,
        class: { type: String, optional: true },
        min: { type: Number, optional: true },
    };
    static defaultProps = { class: "" };
    parseInt(value) {
        return parseInt(value);
    }
}
