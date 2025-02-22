/** @odoo-module */

import { registry } from "@web/core/registry";
import { Many2OneField, many2OneField } from "@web/views/fields/many2one/many2one_field";
import { Component, xml } from "@odoo/owl";

class WizardMany2One extends Many2OneField {

    onExternalBtnClick() {
        this.openDialog(this.resId);
    }
}


export const wizardMany2One = {
    ...many2OneField,
    component: WizardMany2One,
    supportedTypes: ["many2one"],
};

registry.category("fields").add("wizard_mto", wizardMany2One);
