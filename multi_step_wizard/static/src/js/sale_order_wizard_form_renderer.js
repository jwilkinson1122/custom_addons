/** @odoo-module **/

import { FormRenderer } from "@web/views/form/form_renderer";
import { registry } from "@web/core/registry";

export class SaleOrderWizardFormRenderer extends FormRenderer {
  async saveBeforeTabChange() {
    console.log("saveBeforeTabChange called"); // Log method invocation
    if (this.props.record.isInEdition && (await this.props.record.isDirty())) {
      console.log("Record is in edition and has unsaved changes"); // Log condition
      await this.props.record.save();
      console.log("Record saved successfully"); // Log save success
    } else {
      console.log("No changes to save"); // Log no changes
    }
  }

  async onFieldChanged(event) {
    console.log("onFieldChanged called with event:", event); // Log method invocation and event details
    await super.onFieldChanged(event);
    console.log("Field changed:", event.detail.changes); // Log changed fields and values

    if (
      event.detail.changes.start_selected_attribute_value_ids ||
      event.detail.changes.configure_selected_attribute_value_ids
    ) {
      console.log("Refreshing record due to attribute value changes"); // Log specific field change
      await this.props.record.refresh();
      console.log("Record refreshed successfully"); // Log refresh success
    }
  }
}

// Register the renderer globally for the wizard
registry
  .category("form_renderers")
  .add("sale_order_wizard", SaleOrderWizardFormRenderer);

export default SaleOrderWizardFormRenderer;
