/** @odoo-module */

import { registry } from "@web/core/registry";
import { LazyComponent } from "@web/core/assets";
const { Component, xml } = owl;

class ToothSelectFieldLoader extends Component {}

ToothSelectFieldLoader.components = { LazyComponent };
ToothSelectFieldLoader.template = xml`
<LazyComponent bundle="'tooth_select_widget.tooth_telect_ield'" Component="'ToothSelectField'" props="props"/>
`;
ToothSelectFieldLoader.supportedTypes = ["char"];
registry.category("fields").add("tooth_select_field", ToothSelectFieldLoader);