/** @odoo-module **/

import { FormRenderer } from "@web/views/form/form_renderer";
import { registry } from "@web/core/registry";

export class SaleOrderWizardFormRenderer extends FormRenderer {
  async saveBeforeTabChange() {
    if (this.props.record.isInEdition && (await this.props.record.isDirty())) {
      await this.props.record.save();
    }
  }

  async onFieldChanged(event) {
    await super.onFieldChanged(event);
    if (event.detail.changes.start_selected_attribute_value_ids) {
      await this.props.record.refresh(); // Refresh the record to fetch updated values
    }
  }
}

// Register the renderer for the specific view (optional if global override)
registry
  .category("form_renderers")
  .add("sale_order_wizard", SaleOrderWizardFormRenderer);

export default SaleOrderWizardFormRenderer;
