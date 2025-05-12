/** @odoo-module **/
import { Component } from "@odoo/owl";
import ProductTmplAttrib from "./product_tmpl_attrib.esm";

export class ProductAttribGroupRenderer extends Component {}
ProductAttribGroupRenderer.template = "cpq.ProductAttribGroupRenderer";
ProductAttribGroupRenderer.components = { ProductTmplAttrib, ProductAttribGroupRenderer };
ProductAttribGroupRenderer.props = {
    attribute: Object,
    selected: Object,
    side: { type: [String, null], optional: true },
    split: { type: Boolean, optional: true },
    allAttributes: Array,
    onSelect: Function,
    onCustom: Function,
};
