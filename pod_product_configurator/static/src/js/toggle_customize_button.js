/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

class ToggleCustomizeButton extends Component {
    async onClick(ev) {
        ev.preventDefault();

        const stepId = this.props.record.data.step_id;  // assumes step_id is on the record
        const wizardId = this.props.record.resId;

        if (!wizardId || !stepId) return;

        await this.rpc("/web/dataset/call_kw/product.configurator.sale/toggle_customize_step", {
            model: "product.configurator.sale",
            method: "toggle_customize_step",
            args: [],
            kwargs: {
                context: {
                    step_id: stepId,
                    wizard_id: wizardId,
                },
            },
        });

        // Trigger a soft view reload (partial)
        this.props.model.load();
    }

    static template = "pod_product_configurator.ToggleCustomizeButton";
    static props = standardFieldProps;
}
registry.category("fields").add("oe_toggle_customize_step", ToggleCustomizeButton);
