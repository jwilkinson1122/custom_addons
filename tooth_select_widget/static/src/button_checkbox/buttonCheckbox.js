/** @odoo-module **/

import { CheckBox } from "@web/core/checkbox/checkbox";

export class ButtonCheckBox extends CheckBox {
}

ButtonCheckBox.template = "tooth_select_widget.ButtonCheckBox";
ButtonCheckBox.props = {
	    ...CheckBox.props,
	    label: {
	        type: String,
	        optional: true,
	    },
	};