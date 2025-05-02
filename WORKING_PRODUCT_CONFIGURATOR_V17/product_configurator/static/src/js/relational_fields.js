/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Many2OneField } from "@web/views/fields/many2one/many2one_field";
import { StatusField } from "@web/views/fields/status_field";

import { onWillUnmount, status, useComponent, useEnv } from "@odoo/owl";


class CustomFieldStatus extends StatusField {
    _onClickStage(event) {
        this.update(String($(event.currentTarget).data("value")));
    }
}

class CustomMany2OneField extends Many2OneField {
    getFocusableElement() {
        const element = super.getFocusableElement();
        return element || $();
    }
}

registry.category("fields").add("custom_field_status", {
    component: CustomFieldStatus,
});

registry.category("fields").add("custom_many2one_field", {
    component: CustomMany2OneField,
});





// odoo.define("product_configurator.FieldStatus", function (require) {
//     "use strict";

//     var fields = require("web.relational_fields");
//     var FieldStatus = fields.FieldStatus;

//     FieldStatus.include({
//         _onClickStage: function (e) {
//             this._setValue(String($(e.currentTarget).data("value")));
//         },
//     });

//     fields.FieldMany2One.include({
//         getFocusableElement: function () {
//             var element = this._super.apply(this, arguments);
//             if (element === undefined) {
//                 return $();
//             }
//             return element;
//         },
//     });
// });
