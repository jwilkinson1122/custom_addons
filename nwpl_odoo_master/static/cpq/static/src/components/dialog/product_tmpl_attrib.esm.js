/** @odoo-module */

import { onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { getVisibleValueMap, getSelectedBucket } from "./utils.esm";
const { Component } = owl;

class ProductTmplAttrib extends Component {

    static props = {
        attribute: { type: Object },
        selected: { type: Object, optional: true },
        side: { type: String, optional: true },
        hideLabel: { type: Boolean, optional: true },
        onSelect: { type: Function, optional: true },
        onCustom: { type: Function, optional: true },
    };

    // setup() {
    //     super.setup(...arguments);
    //     this.user = useService("user");
    //     onWillStart(this.onWillStart);
    // }

    
    setup() {
        const attr = this.props.attribute || {};
        const id = Number(attr.id ?? 0) || 0;

        const raw = Array.isArray(attr.values) && attr.values.length
        ? attr.values
        : (Array.isArray(attr.ptav_ids) ? attr.ptav_ids : []);

        const values = (raw || []).map((v) => {
        if (v && typeof v === "object") return { ...v, id: Number(v.id ?? v[0] ?? v) };
        if (Array.isArray(v)) return { id: Number(v[0]), name: v[1] };
        return { id: Number(v) };
        }).filter(v => Number.isFinite(v.id));

        // keep a normalized copy the templates can read
        this.attribute = { ...attr, id, values };
    }

    get selectedIds() {
        const sel = this.props.selected || {};
        return Object.keys(sel).map(String);
    }

    async onWillStart() {
        console.log(
            `[ProductTmplAttrib] Rendering "${this.props.attribute?.name}" (side=${this.props.side})`
        );
        console.log("[PTA] props.selected:", this.props.selected);
        console.log(
            "[PTA] Is root object?",
            this.props.selected &&
                "left" in this.props.selected &&
                "right" in this.props.selected &&
                "shared" in this.props.selected
        );
        console.log("[PTA] side:", this.props.side);
        console.log("[PTA] this.bucket:", this.bucket);
        console.log(
            "[PTA][selected] keys:",
            Object.keys(this.props.selected || {}),
            "side:",
            this.props.side
        );
    }

    // ---- helpers ----
    get isGroup() {
        const a = this.props.attribute || {};
        return !!(a.is_group || (a.children && Array.isArray(a.children) && !a.values));
    }

    get bucket() {
        // If the parent accidentally passed the ROOT {left,right,shared} object, pick the right bucket.
        if (
            typeof this.props.selected === "object" &&
            this.props.selected &&
            "left" in this.props.selected &&
            "right" in this.props.selected &&
            "shared" in this.props.selected
        ) {
            console.error(
                "[BUG] ProductTmplAttrib got root object instead of bucket for",
                this.props.attribute?.name,
                this.props.side
            );
            return this.props.selected[this.props.side || "shared"] || {};
        }
        return this.props.selected || {};
    }

    stringify() {
        return JSON.stringify(this.props.attribute);
    }

    getPTAVTemplate() {
        // If this is a group node, do not try to render a leaf control.
        if (this.isGroup) {
            return null;
        }
        switch (this.props.attribute?.display_type) {
            case "color":
                return "cpq.ProductTmplAttrib-color";
            case "pills":
            case "radio":
            default:
                return "cpq.ProductTmplAttrib-radio";
        }
    }

    getVisibleValues() {
        // Groups or attributes without values: render nothing.
        const attr = this.props.attribute || {};
        // if (!attr.values || !Array.isArray(attr.values) || this.isGroup) {
        //     return [];
        // }
        if (!Array.isArray(attr.values) || !attr.values.every(v => typeof v === 'object')) {
            console.warn("[PTA] Invalid values in attribute:", attr);
            return [];
        }


        const selected = this.bucket;
        const valueMap = getVisibleValueMap(
            attr,
            selected,
            this.props.allAttributes || []
        );

        console.debug("Selected bucket:", selected);
        for (const val of valueMap) {
            console.debug(`  Value:`, val);
        }
        console.groupEnd?.();

        return valueMap;
    }

    get selectedIds() {
        const sel = this.bucket || {};
        console.log("selectedIds keys:", Object.keys(sel || {}));

        // Get keys from the (possibly proxied) object
        let keys = [];
        try {
            keys = Object.keys(sel || {});
            if (keys.length === 0 && sel) {
                keys = Object.getOwnPropertyNames(sel);
            }
        } catch (e) {}
        console.log("[selectedIds] Fallback keys:", keys);

        const values = this.props.attribute?.values || [];
        if (!Array.isArray(values) || values.length === 0) {
            return [];
        }

        // Map any acceptable key -> canonical PTAV id (v.id)
        // Accept both v.id and v.x_virtual_cpq_id as lookup keys.
        const keyToPtav = new Map();
        for (const v of values) {
            const ptavId = String(v.id);
            keyToPtav.set(ptavId, ptavId);
            const virtId =
                v.x_virtual_cpq_id != null ? String(v.x_virtual_cpq_id) : null;
            if (virtId) keyToPtav.set(virtId, ptavId);
        }

        const out = [];
        for (const rawKey of keys) {
            const key = String(rawKey);
            if (!keyToPtav.has(key)) continue; // not a key for this attribute

            const entry = sel[rawKey];
            if (entry === false || entry == null) continue;

            // Normalize whatever is stored to a canonical PTAV id
            const pushCanonical = (candidate) => {
                const s = String(candidate);
                out.push(keyToPtav.get(s) || s); // prefer canonical, fallback to given
            };

            if (entry === true) {
                pushCanonical(key);
                continue;
            }
            if (typeof entry === "object") {
                const candidate = entry.id ?? entry.value ?? key;
                pushCanonical(candidate);
                continue;
            }
            // primitive
            pushCanonical(entry);
        }

        // de-dupe while keeping order stable
        const ids = [...new Set(out)];
        console.log("[selectedIds] Final selectedIds (as string):", ids);
        return ids;
    }

    get selectedValue() {
        const selected = this.bucket;
        for (const v of this.getVisibleValues()) {
            const ptavId = String(v.id);
            const virtId = v.x_virtual_cpq_id ? String(v.x_virtual_cpq_id) : null;
            for (const key of [ptavId, virtId]) {
                if (!key) continue;
                const val = selected[key];
                if (val === undefined) continue;
                if (val === true) return v;
                if (typeof val === "object") {
                    if (val.id && (val.id === v.id || val.id == v.id)) return v;
                    if (val.value && (val.value === v.id || val.value == v.id)) return v;
                }
                if (val === v.id || val === v.value) return v;
            }
        }
        return null;
    }

    isValueSelected(ptav) {
        const selected = this.bucket || {};
        const ptavId = String(ptav.id);
        const virtId = ptav.x_virtual_cpq_id ? String(ptav.x_virtual_cpq_id) : null;

        let result = false;
        for (const key of [ptavId, virtId]) {
            if (!key) continue;
            const val = selected[key];
            if (val === undefined) continue;
            if (val === true) result = true;
            if (typeof val === "object") {
                if (val.id && (val.id === ptav.id || val.id == ptav.id)) result = true;
                if (val.value && (val.value === ptav.id || val.value == ptav.id))
                    result = true;
            }
            if (val === ptav.id || val === ptav.value) result = true;
        }

        console.log(
            `[ProductTmplAttrib][isValueSelected] attribute="${this.props.attribute?.name}" ptav.id=${ptav.id} side=${this.props.side || "shared"}`,
            "selected keys=",
            Object.keys(selected || {}),
            "selected object:",
            selected,
            "RETURN:",
            result
        );

        return result;
    }

    isSelectedPTAVCustom() {
        return false;
    }
}

ProductTmplAttrib.template = "cpq.ProductTmplAttrib";

// 🔧 Loosened schema: allow group nodes and optional leaf fields
ProductTmplAttrib.props = {
    id: Number,
    attribute: {
        type: Object,
        shape: {
            // groups might not have numeric id
            id: { type: [Number, String], optional: true },
            name: String,

            // groups won't have a display_type
            display_type: {
                type: String,
                optional: true,
                validate: (type) =>
                    ["color", "pills", "radio", "select"].includes(type),
            },

            is_group: { type: Boolean, optional: true },
            required: { type: Boolean, optional: true },
            sequence: { type: Number, optional: true },

            // groups can have children
            children: { type: Array, optional: true },

            // leaf attributes have values
            values: {
                type: Array,
                optional: true,
                element: {
                    id: [Number, String],
                    name: String,
                    html_color: [Boolean, String],
                    is_custom: [Boolean],
                    price_extra: [Number],
                    excluded: { type: Boolean, optional: true },
                    cpq_custom_type: [Boolean, String],
                    triggers: { type: Array, optional: true },
                    children: { type: Array, optional: true },
                    linked_option_id: { type: [Object, false], optional: true },

                    // commonly used in your logic
                    x_virtual_cpq_id: { type: [Number, String], optional: true },
                    value: { type: [Number, String], optional: true },
                },
            },
        },
    },
    selected: {
        type: Object,
        optional: true,
        validate: (sel) => {
            if (
                sel &&
                typeof sel === "object" &&
                "left" in sel &&
                "right" in sel &&
                "shared" in sel
            ) {
                console.error(
                    "[ProductTmplAttrib.props] ❌ Invalid selected passed — expected bucket, received root:",
                    sel
                );
                return false;
            }
            return true;
        },
    },
    side: { type: String, optional: true },
    hideLabel: { type: Boolean, optional: true },
    onSelect: { type: "function" },
    onCustom: { type: "function" },
};

export default ProductTmplAttrib;
