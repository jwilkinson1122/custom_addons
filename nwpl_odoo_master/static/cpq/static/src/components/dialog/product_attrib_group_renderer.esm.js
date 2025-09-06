/** @odoo-module **/
import { Component } from "@odoo/owl";
import ProductTmplAttrib from "./product_tmpl_attrib.esm";
import { getSafeSelectedBucket } from "./utils.esm";

export class ProductAttribGroupRenderer extends Component {

    // Remove setup entirely, or just keep logging if you like
    // setup() {
    //     this.getSelectedBucket = getSelectedBucket;
    //     // REMOVE all assignments here
    // }


    constructor(...args) {
        super(...args);
        console.log("[PAGR] props.selected:", this.props.selected);
        console.log("[PAGR] flatSelected:", this.flatSelected);
        console.log("[PAGR] leftSelected:", this.leftSelected);
        console.log("[PAGR] rightSelected:", this.rightSelected);

    }

    // Returns the correct "bucket" for the current node
    get flatSelected() {
        // Full selected object (root)
        if (typeof this.props.selected === "object" &&
            "left" in this.props.selected &&
            "right" in this.props.selected &&
            "shared" in this.props.selected) {
            return this.props.selected[this.props.side || "shared"] || {};
        }
        // Already a bucket
        return this.props.selected || {};
    }
    get leftSelected() {
        if (typeof this.props.selected === "object" &&
            "left" in this.props.selected && "right" in this.props.selected) {
            return this.props.selected.left || {};
        }
        return {};
    }
    get rightSelected() {
        if (typeof this.props.selected === "object" &&
            "left" in this.props.selected && "right" in this.props.selected) {
            return this.props.selected.right || {};
        }
        return {};
    }

    normalizeAttribute(attr) {
        if (!attr) return { id: 0, name: "", values: [] };
        const id = Number(attr.id ?? attr.attribute_id ?? 0) || 0;

        // Prefer objects in `values`, else fall back to `ptav_ids`
        const raw = Array.isArray(attr.values) && attr.values.length
            ? attr.values
            : (Array.isArray(attr.ptav_ids) ? attr.ptav_ids : []);

        const values = (raw || []).map((v) => {
            if (v && typeof v === "object") {
                // coerce id to number if needed
                return { ...v, id: Number(v.id ?? v[0] ?? v) };
            }
            if (Array.isArray(v)) return { id: Number(v[0]), name: v[1] };
            return { id: Number(v) };
        }).filter(v => Number.isFinite(v.id));

        return { ...attr, id, values };
    }


}

ProductAttribGroupRenderer.template = "cpq.ProductAttribGroupRenderer";
ProductAttribGroupRenderer.components = { ProductTmplAttrib, ProductAttribGroupRenderer };
ProductAttribGroupRenderer.props = {
    attribute: Object,
    selected: Object,
    side: { type: [String, null], optional: true },
    split: { type: Boolean, optional: true },
    splitByAttrMap: { type: Object, optional: true },
    onToggleSplit: { type: Function, optional: true },
    allAttributes: Array,
    onSelect: Function,
    onCustom: Function,
    laterality: String,
};

