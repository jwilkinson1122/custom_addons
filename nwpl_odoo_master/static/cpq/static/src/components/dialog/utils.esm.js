/** @odoo-module **/
import { useService } from "@web/core/utils/hooks";
import { onWillUnmount } from "@odoo/owl";

// =============================
// SHAPE & STRUCTURE UTILITIES
// =============================

export function safeParse(obj) {
    if (!obj) return {};
    if (typeof obj === "string") {
        try { return JSON.parse(obj); } catch { return {}; }
    }
    return obj;
}


export function ensureStringKeys(obj) {
    const out = {};
    for (const k in obj) {
        out[String(k)] = obj[k];
    }
    return out;
}

export function getSelectedBucket(selected, side) {
    if (!selected || typeof selected !== "object") return {};
    if (side === 'left' || side === 'right') {
        // Return attribute-based selections for the side
        return selected[side] || {};
    }
    // Fallback to shared if not split mode
    return selected.shared || {};  
}

export function deepPlainClone(obj) {
    // Recursively copies only own enumerable properties
    if (Array.isArray(obj)) {
        return obj.map(deepPlainClone);
    } else if (obj && typeof obj === "object") {
        const result = {};
        for (const key of Object.keys(obj)) {
            result[key] = deepPlainClone(obj[key]);
        }
        return result;
    }
    return obj;
}


export function getSafeSelectedBucket(selected, side = 'shared', label = 'unknown') {
    if (!selected || typeof selected !== 'object') return {};

    if ('left' in selected && 'right' in selected && 'shared' in selected) {
        console.warn(
            `[getSafeSelectedBucket] ⚠️ Detected root selected object. Extracting bucket for side='${side}' [source: ${label}]`,
            selected
        );
        return deepPlainClone(getSelectedBucket(selected, side));
    }

    return deepPlainClone(selected);
}

/**
 * Returns a canonical PTAV dict for all side buckets.
 * All values guaranteed to be {id, value} objects.
 * No mutation.
 */

// export function expandPtavDicts(selected) {
//     const output = {};
//     for (const bucket of ["left", "right", "shared"]) {
//         if (selected && selected[bucket]) {
//             output[bucket] = {};
//             for (const [attrId, attrValues] of Object.entries(selected[bucket])) {
//                 output[bucket][attrId] = {}; 
//                 for (const [ptavIdStr, ptavObj] of Object.entries(attrValues)) {
//                     output[bucket][attrId][ptavIdStr] = {
//                         id: parseInt(ptavIdStr, 10),
//                         value: parseInt(ptavIdStr, 10),
//                         ...ptavObj,
//                     };
//                 }
//             }
//         }
//     }
//     return output;
// }

export function expandPtavDicts(selected) {
    // Input shape (per bucket): { [ptavId]: metaOrScalar }
    // Output shape (same keys): { [ptavId]: { id, value, ...meta } }
    const out = {};
    for (const bucket of ["left", "right", "shared"]) {
        if (!selected || !selected[bucket]) continue;
        const src = selected[bucket];
        const dst = {};
        for (const [ptavIdStr, val] of Object.entries(src)) {
            const id = parseInt(ptavIdStr, 10);
            if (!Number.isFinite(id)) continue;

            if (val && typeof val === "object" && !Array.isArray(val)) {
                // Already an object → normalize & keep extras
                const normalized = {
                    id,
                    value: ("value" in val && val.value !== undefined) ? val.value : id,
                    ...val,
                };
                // force canonical numeric id/value
                normalized.id = id;
                if (typeof normalized.value !== "number") {
                    const maybeNum = parseInt(normalized.value, 10);
                    normalized.value = Number.isFinite(maybeNum) ? maybeNum : normalized.value;
                }
                dst[ptavIdStr] = normalized;
            } else {
                // Scalar/boolean → lift to object
                dst[ptavIdStr] = { id, value: id };
            }
        }
        out[bucket] = dst;
    }
    return out;
}



/**
 * Legacy compatibility, use expandPtavDicts for future code.
 */
export function expandSharedDictToPtavDict(selected) {
    if (selected && selected.shared) {
        for (const [k, v] of Object.entries(selected.shared)) {
            if (typeof v !== "object" || v === null) {
                selected.shared[k] = { id: parseInt(k, 10), value: parseInt(k, 10) };
            }
        }
    }
    return selected;
}


// Ensure required attributes have at least one choice when nothing is selected / no prefs exist
export function ensureDefaultsForRequired(selected, ptalIds = [], { split = false, laterality = "bilateral" } = {}) {
    // Start from a canonical bucket shape
    const buckets = canonicalizeSelectedBuckets(selected || {}, split, laterality);

    // Flatten to just attributes (skip groups)
    const attrs = flattenAttributes(ptalIds);

    // Helper: do we already have a choice for this attribute in a given bucket?
    function hasChoiceForAttr(bucket = {}, attr) {
        const ids = new Set((attr.ptav_ids || attr.values || []).map(v => String(v.id)));
        return Object.keys(bucket).some(k => ids.has(String(k)));
    }

    // Helper: pick the first non-excluded option (you can swap this for “cheapest” if you expose prices)
    function pickFirstAllowed(attr) {
        const vals = (attr.ptav_ids || attr.values || []).filter(v => !v.excluded);
        return vals.length ? vals[0] : null;
    }

    for (const attr of attrs) {
        if (!attr.required) continue;

        if (laterality === "bilateral" && !split) {
            if (!hasChoiceForAttr(buckets.shared, attr)) {
                const v = pickFirstAllowed(attr);
                if (v) buckets.shared[String(v.id)] = { id: v.id, value: v.id };
            }
        } else if (laterality === "bilateral" && split) {
            if (!hasChoiceForAttr(buckets.left, attr)) {
                const v = pickFirstAllowed(attr);
                if (v) buckets.left[String(v.id)] = { id: v.id, value: v.id };
            }
            if (!hasChoiceForAttr(buckets.right, attr)) {
                const v = pickFirstAllowed(attr);
                if (v) buckets.right[String(v.id)] = { id: v.id, value: v.id };
            }
        } else if (laterality === "left") {
            if (!hasChoiceForAttr(buckets.left, attr)) {
                const v = pickFirstAllowed(attr);
                if (v) buckets.left[String(v.id)] = { id: v.id, value: v.id };
            }
        } else if (laterality === "right") {
            if (!hasChoiceForAttr(buckets.right, attr)) {
                const v = pickFirstAllowed(attr);
                if (v) buckets.right[String(v.id)] = { id: v.id, value: v.id };
            }
        }
    }

    return buckets;
}


/**
 * Compresses bilateral shared selections into the minimal shape.
 * Returns: {shared}, {left/right}, or a mix, never mutates input.
 */
export function compressSharedSelections(selected, laterality, isSplitMode) {
    if (!selected.left || !selected.right || laterality !== "bilateral" || isSplitMode) {
        return { ...selected };
    }
    const shared = {};
    const leftOnly = {};
    const rightOnly = {};
    for (const ptavId of Object.keys(selected.left)) {
        const l = selected.left[ptavId];
        const r = selected.right[ptavId];
        if (l && r && JSON.stringify(l) === JSON.stringify(r)) {
            shared[ptavId] = { ...l, shared: true };
        } else {
            leftOnly[ptavId] = l;
        }
    }
    for (const ptavId of Object.keys(selected.right)) {
        if (!shared[ptavId] && !leftOnly[ptavId]) {
            rightOnly[ptavId] = selected.right[ptavId];
        }
    }
    if (Object.keys(shared).length && !Object.keys(leftOnly).length && !Object.keys(rightOnly).length) {
        return { shared };
    }
    return {
        ...(Object.keys(shared).length ? { shared } : {}),
        ...(Object.keys(leftOnly).length ? { left: leftOnly } : {}),
        ...(Object.keys(rightOnly).length ? { right: rightOnly } : {}),
    };
}

/**
 * Canonically flattens a selection for backend use, always numeric keys.
 * Accepts any hybrid or legacy input.
 */

export function flattenSelectedToBackendDict(selected, split = false, laterality = "bilateral") {
    if (!selected) return {};

    const flat = {};
    if (split) {
        for (const side of ['left', 'right']) {
            const sideData = selected[side] || {};
            for (const ptavId in sideData) {
                flat[`${side}:${ptavId}`] = sideData[ptavId];
            }
        }
        return flat;
    }
    // Not split
    const sharedData = selected.shared || {};
    for (const ptavId in sharedData) {
        flat[ptavId] = sharedData[ptavId];
    }
    return flat;
}

/**
 * Flattens any CPQ combination to {selected:...}, {left:...}, {right:...}
 * Always returns minimal.
 */
export function flattenCombination(selected, laterality = "bilateral", split = false) {
    if (laterality === "bilateral" && !split && selected.shared) {
        return { selected: { ...selected.shared } };
    }
    if (
        laterality === "bilateral" &&
        split &&
        ((selected.left && Object.keys(selected.left).length) || (selected.right && Object.keys(selected.right).length))
    ) {
        return {
            ...(selected.left ? { left: { ...selected.left } } : {}),
            ...(selected.right ? { right: { ...selected.right } } : {}),
        };
    }
    if (laterality === "left" && selected.left && Object.keys(selected.left).length) {
        return { selected: { ...selected.left } };
    }
    if (laterality === "right" && selected.right && Object.keys(selected.right).length) {
        return { selected: { ...selected.right } };
    }
    if (!selected.left && !selected.right && !selected.shared && Object.keys(selected).length) {
        return { selected: { ...selected } };
    }
    return { selected: {} };
}

/**
 * Recursively flattens attribute groups into a flat array.
 */
export function flattenAttributes(ptalIds) {
    // Recursively flatten a tree of attribute groups to just an array of attribute objects (not values)
    let flat = [];
    for (const attr of ptalIds || []) {
        if (attr.is_group && Array.isArray(attr.children)) {
            flat = flat.concat(flattenAttributes(attr.children));
        } else {
            flat.push(attr);
        }
    }
    return flat;
}

/**
 * Flattens grouped split selection into a flat selection.
 */

export function flattenGroupedSelection(grouped) {
    // Defensive: ensure always returns { left, right, shared }
    if (!grouped || typeof grouped !== "object") {
        return { left: {}, right: {}, shared: {} };
    }
    // If already has the three buckets, just deep-clone them
    if ("left" in grouped || "right" in grouped || "shared" in grouped) {
        return {
            left: { ...(grouped.left || {}) },
            right: { ...(grouped.right || {}) },
            shared: { ...(grouped.shared || {}) },
        };
    }
    // Otherwise, treat it as a flat dict—wrap as shared
    return { left: {}, right: {}, shared: { ...grouped } };
}


/**
 * Returns a sanitized, always-present {left,right,shared} structure with only numeric keys.
 */
export function sanitizeSelectedForBackend(selected) {
    function clean(obj) {
        const out = {};
        for (const k in obj) if (/^\d+$/.test(k)) out[k] = obj[k];
        return out;
    }
    if (selected.left || selected.right || selected.shared) {
        return {
            left: clean(selected.left || {}),
            right: clean(selected.right || {}),
            shared: clean(selected.shared || {}),
        };
    }
    return clean(selected);
}

export function canonicalizePrefSelected(prefSelected, ptalIds=[]) {
    const result = {};
    for (const key of Object.keys(prefSelected)) {
        const val = prefSelected[key];

        // Try to find PTAV for note fallback
        let ptavNote = "";
        let ptavObj = null;
        for (const attr of ptalIds) {
            ptavObj = (attr.ptav_ids || attr.values || []).find(v => String(v.id) === String(key));
            if (ptavObj && ptavObj.note) {
                ptavNote = ptavObj.note;
                break;
            }
        }

        // If a note is provided in the preference object, use it, else use ptavNote
        let note = (val && val.note) || ptavNote;

        // If a preference object is present (object with id), use/extend it
        if (typeof val === "object" && val !== null && "id" in val) {
            result[key] = {
                ...val,
                isPreferred: val.isPreferred || false,
                isPreferredLeft: val.isPreferredLeft !== undefined ? val.isPreferredLeft : (val.isPreferred || false),
                isPreferredRight: val.isPreferredRight !== undefined ? val.isPreferredRight : (val.isPreferred || false),
                note: note || "",
            };
        } else {
            // Default all true if only value is present
            result[key] = {
                id: parseInt(key, 10),
                value: parseInt(key, 10),
                isPreferred: true,
                isPreferredLeft: true,
                isPreferredRight: true,
                note: note || "",
            };
        }
    }
    return result;
}

/**
 * Produces canonical structure for all modes (split/shared/unilateral).
 */
export function setCanonicalSelected(selected, split, laterality) {
    return sanitizeSelectedForBackend(
        normalizeSelectedStructure({ selected, split, laterality }).selected
    );
}

export function canonicalizeInitialSelected(config) {
    // Accepts config as loaded from backend
    const isSplit = config.split || Object.values(config.splitByAttrMap || {}).some(Boolean);
    const laterality = config.laterality || "bilateral";
    return normalizeSelectedStructure({
        selected: config.selected,
        split: isSplit,
        laterality,
    }).selected;
}

export function canonicalizeSelectedBuckets(selected, split, laterality) {
    let out = { left: {}, right: {}, shared: {} };
    if (split && laterality === "bilateral") {
        if (selected.shared && Object.keys(selected.shared).length &&
            (!selected.left || !Object.keys(selected.left).length) &&
            (!selected.right || !Object.keys(selected.right).length)
        ) {
            out.left = { ...selected.shared };
            out.right = { ...selected.shared };
        } else {
            out.left = selected.left || {};
            out.right = selected.right || {};
        }
        out.shared = {};
    } else if (laterality === "left") {
        out.left = selected.left || selected || {};
    } else if (laterality === "right") {
        out.right = selected.right || selected || {};
    } else {
        out.shared = selected.shared || selected || {};
    }
    return out;
}


/**
 * Returns config.selected as a canonical structure for its mode.
 */

export function normalizeSelectedStructure(config) {
    let selected = JSON.parse(JSON.stringify(config.selected || {}));
    const { split, laterality } = config;
    const hasBuckets = typeof selected === "object" && ("left" in selected || "right" in selected);
    const hasShared = typeof selected === "object" && "shared" in selected;
    const isFlat = typeof selected === "object" && !hasBuckets && !hasShared && Object.keys(selected).length > 0;

    if (laterality === "left") {
        config.selected = { left: { ...(selected.left || (isFlat ? selected : {})) } };
    } else if (laterality === "right") {
        config.selected = { right: { ...(selected.right || (isFlat ? selected : {})) } };
    } else if (laterality === "bilateral") {
        if (split) {
            config.selected = {
                left: { ...(selected.left || (isFlat ? selected : {})) },
                right: { ...(selected.right || (isFlat ? selected : {})) },
                shared: {},
            };
        } else {
            // ----------- REVISED LOGIC BELOW -----------
            if (hasShared) {
                // If we already have a shared bucket, preserve it (preference-driven)
                config.selected = { left: {}, right: {}, shared: selected.shared || {} };
            } else if (isFlat) {
                // Flat dict: treat as shared
                config.selected = { left: {}, right: {}, shared: { ...selected } };
            } else if (hasBuckets) {
                // Only collapse to shared if left/right both have identical selections (rare legacy case)
                const left = selected.left || {};
                const right = selected.right || {};
                const shared = {};
                Object.keys(left).forEach(ptavId => {
                    if (right[ptavId] && JSON.stringify(left[ptavId]) === JSON.stringify(right[ptavId])) {
                        shared[ptavId] = left[ptavId];
                    }
                });
                config.selected = { left: {}, right: {}, shared };
            }
            // ----------- END REVISED LOGIC -----------
        }
    }
    // Defensive: always ensure keys are present in bilateral
    if (laterality === "bilateral") {
        config.selected.left = config.selected.left || {};
        config.selected.right = config.selected.right || {};
        config.selected.shared = config.selected.shared || {};
    }

    return config;
}

/**
 * Safely prepares configurator values for Odoo sale.order.line write.
 * - Flattens "selected" if nested.
 * - Always includes grouped, ptal_ids, splitByAttrMap, cpqPreferences, etc.
 * - Ensures all required summary fields are present.
 * - Accepts an optional version for future-proofing.
 * - Optionally post-processes config (e.g. for extra custom fields).
 *
 * @param {Object} config - The dialog config state/result.
 * @param {number|string|undefined} fallbackUomId - Used if config.product_uom not set.
 * @param {Object} [opts] - { version: string, postProcess: (config) => config }
 * @returns {Object} Patch dict for sale.order.line (to use with write/update)
 */
export function getSafeConfiguratorValues(config, fallbackUomId, opts = {}) {
    let safeConfig;
    try {
        // Deep clone to avoid mutating dialog config in memory
        safeConfig = JSON.parse(JSON.stringify(config || {}));
    } catch (err) {
        console.error("Failed to clone configurator config:", err, config);
        safeConfig = { ...config }; // fallback: shallow
    }

    // Clean up any possible legacy or nested 'selected' shapes
    let selected = safeConfig.selected;
    // Flatten out .selected.selected (broken nesting from old code)
    if (selected?.selected) {
        console.warn("[CPQ] Detected nested selected in config. Flattening...");
        selected = selected.selected;
    }
    // Defensive: force empty object if selected still not correct
    if (typeof selected !== "object" || Array.isArray(selected) || !selected) {
        selected = {};
    }
    safeConfig.selected = selected;

    // Defensive: Always carry over grouped if present (sometimes JS state doesn't sync to backend cleanly)
    if (!safeConfig.grouped && (safeConfig.selected?.left || safeConfig.selected?.right || safeConfig.selected?.shared)) {
        safeConfig.grouped = {
            left: safeConfig.selected.left || {},
            right: safeConfig.selected.right || {},
            shared: safeConfig.selected.shared || {},
        };
    }

    // Carry over ptal_ids (attribute lines), preferences, split map, etc.
    // if (config.ptal_ids && !safeConfig.ptal_ids) safeConfig.ptal_ids = config.ptal_ids;
    safeConfig.ptal_ids = config.ptal_ids || [];
    if (config.cpqPreferences && !safeConfig.cpqPreferences) safeConfig.cpqPreferences = config.cpqPreferences;
    if (config.splitByAttrMap && !safeConfig.splitByAttrMap) safeConfig.splitByAttrMap = config.splitByAttrMap;

    // Always include laterality and split flags
    safeConfig.laterality = safeConfig.laterality || "bilateral";
    safeConfig.split = Boolean(safeConfig.split);

    // Defensive: Always ensure correct types
    const quantity = Number(safeConfig.quantity_to_make || safeConfig.product_uom_qty || 1) || 1;
    const uomId = safeConfig.product_uom || fallbackUomId || null;
    const priceUnit =
        Number(safeConfig.price_unit) ||
        (Number(safeConfig.total_price) && quantity ? Number(safeConfig.total_price) / quantity : 0);

    // Optionally allow post-processing for new fields
    if (typeof opts.postProcess === "function") {
        safeConfig = opts.postProcess(safeConfig) || safeConfig;
    }

    // Always include version if passed for future compatibility
    if (opts.version) {
        safeConfig._config_version = opts.version;
    }

    // Clean up common serialization gotchas
    try {
        // Remove any possible circular structures or unserializable fields
        JSON.stringify(safeConfig);
    } catch (err) {
        console.error("Configurator config not serializable!", err, safeConfig);
        // Fallback: strip non-serializable props
        safeConfig = JSON.parse(JSON.stringify(safeConfig, (k, v) => {
            if (typeof v === "function" || typeof v === "symbol") return undefined;
            return v;
        }));
    }

    return {
        product_uom_qty: quantity,
        ...(uomId ? { product_uom: uomId } : {}),
        price_unit: priceUnit,
        name: safeConfig.name || "Configured Product",
        cpq_configuration_json: JSON.stringify(safeConfig),
        cpq_configuration_summary: safeConfig.configuration_summary || "",
    };
}

export function enrichSelectedWithPreferred(selected, ptalList = []) {
    const enriched = JSON.parse(JSON.stringify(selected || {}));

    // Helper: check per-side preferred flags for a PTAV.
    function getPreferredFlags(attrId, ptavId, ptalList) {
        let isPreferredLeft = false;
        let isPreferredRight = false;
        let isPreferredShared = false;
        for (const ptal of ptalList) {
            if (ptal.id !== attrId) continue;
            for (const ptav of ptal.ptav_ids || ptal.values || []) {
                if (ptav.id === parseInt(ptavId)) {
                    if (ptav.isPreferredLeft !== undefined)
                        isPreferredLeft = !!ptav.isPreferredLeft;
                    if (ptav.isPreferredRight !== undefined)
                        isPreferredRight = !!ptav.isPreferredRight;
                    if (ptav.isPreferred !== undefined)
                        isPreferredShared = !!ptav.isPreferred;
                }
            }
        }
        return { isPreferredLeft, isPreferredRight, isPreferred: isPreferredShared };
    }

    for (const ptal of ptalList || []) {
        for (const ptav of ptal.ptav_ids || ptal.values || []) {
            const ptavId = String(ptav.id);
            const flags = getPreferredFlags(ptal.id, ptavId, ptalList);

            if ("left" in enriched || "right" in enriched) {
                if (enriched.left?.[ptavId] !== undefined) {
                    enriched.left[ptavId].isPreferredLeft = flags.isPreferredLeft || flags.isPreferred;
                }
                if (enriched.right?.[ptavId] !== undefined) {
                    enriched.right[ptavId].isPreferredRight = flags.isPreferredRight || flags.isPreferred;
                }
            } else if (enriched?.[ptavId] !== undefined) {
                // Shared (legacy)
                enriched[ptavId].isPreferred = flags.isPreferred;
            }
        }
    }
    return enriched;
}

export function enrichPtalIdsWithPreferences(ptalIds, prefDetails) {
    for (const groupOrAttr of ptalIds) {
        const children = groupOrAttr.is_group ? groupOrAttr.children : [groupOrAttr];
        for (const attr of children) {
            const ptavList = attr.ptav_ids || attr.values || [];
            const updatedValues = ptavList.map((val) => {
                const valId = parseInt(val.id);
                // Find *all* matches for this attribute/value pair
                const matches = prefDetails.filter(
                    (p) =>
                        parseInt(p.attribute_id) === attr.id &&
                        (parseInt(p.ptav_id) === valId || parseInt(p.value_id) === valId)
                );
                // Mark as preferred per-side (if in rules)
                const isPreferredLeft = matches.some(m =>
                    m.laterality === "left" || m.laterality === "bilateral"
                );
                const isPreferredRight = matches.some(m =>
                    m.laterality === "right" || m.laterality === "bilateral"
                );
                // For shared (legacy), mark as preferred only if both sides prefer
                const isPreferred = isPreferredLeft && isPreferredRight;
                return {
                    ...val,
                    isPreferredLeft,
                    isPreferredRight,
                    isPreferred,
                    note: matches[0]?.note || "",
                    linked_option_id: val.linked_option_id || undefined,
                };
            });
            if (attr.ptav_ids) attr.ptav_ids = updatedValues;
            else if (attr.values) attr.values = updatedValues;
        }
    }
}

export function mergeSelectedWithFallback(selected = {}, fallback = {}) {
    // Helper to check if this is a "split" structure
    const isSplit = (obj) =>
        obj && (obj.left !== undefined || obj.right !== undefined);

    // Helper to wrap flat objects under shared
    function wrapFlatAsShared(obj) {
        if (!obj) return { left: {}, right: {}, shared: {} };
        if (isSplit(obj)) return obj;
        // Already has left/right/shared? (shared is okay to be empty)
        if (obj.shared !== undefined) return obj;
        // If this is a flat object (e.g. {3: true, 8: true}), wrap under shared
        return { left: {}, right: {}, shared: obj };
    }

    selected = wrapFlatAsShared(selected);
    fallback = wrapFlatAsShared(fallback);

    // Merge one side, keeping all preferred keys per-side if present
    function mergeSide(sideSelected = {}, sideFallback = {}) {
        const result = {};
        // Add fallback (from preferences)
        for (const [key, val] of Object.entries(sideFallback)) {
            if (val === true) {
                result[key] = { 
                    id: parseInt(key, 10), 
                    value: parseInt(key, 10),
                    // Assume fallback is for "preferred"; mark all as true for legacy
                    isPreferred: true,
                    isPreferredLeft: true,
                    isPreferredRight: true,
                };
            } else if (typeof val === 'object') {
                result[key] = { ...val };
            } else {
                result[key] = { id: parseInt(key, 10), value: val };
            }
        }
        // Override with selected (user choice wins)
        for (const [key, val] of Object.entries(sideSelected)) {
            result[key] = (typeof val === 'object')
                ? { ...val }
                : { id: parseInt(key, 10), value: val };
        }
        return result;
    }

    // Final output: always include left/right/shared
    return {
        left: mergeSide(selected.left, fallback.left),
        right: mergeSide(selected.right, fallback.right),
        shared: mergeSide(selected.shared, fallback.shared),
    };
}

export function ensureSelectedObjectsFull(selected) {
    if (!selected) return {};
    if (selected.left !== undefined || selected.right !== undefined) {
        return {
            left: ensureSelectedObjects(selected.left || {}),
            right: ensureSelectedObjects(selected.right || {}),
        };
    }
    return ensureSelectedObjects(selected);
}

export function ensureSelectedObjects(selected) {
    const result = {};
    for (const [k, v] of Object.entries(selected || {})) {
        if (typeof v === "object" && v !== null && v.value !== undefined) {
            result[k] = { ...v };
        } else {
            result[k] = { id: parseInt(k, 10), value: v };
        }
    }
    return result;
}

export function stripFallbackMetadata(selected) {
    const clean = JSON.parse(JSON.stringify(selected));
    function cleanSide(side) {
        for (const key of Object.keys(side || {})) {
            const val = side[key];
            // Remove orphaned fallback/empty keys
            if ((val?.isPreferred || val?.isPreferredLeft || val?.isPreferredRight) && !val?.value) {
                delete side[key];
            } else if (typeof val === "object") {
                delete val.isPreferred;
                delete val.isPreferredLeft;
                delete val.isPreferredRight;
                delete val.note;
            }
        }
    }
    if (clean.left || clean.right) {
        cleanSide(clean.left);
        cleanSide(clean.right);
    } else {
        cleanSide(clean);
    }
    return clean;
}

// =============================
// CPQ FRONTEND AND PAYLOAD HELPERS
// =============================

export function computeLocalCPQPriceBreakdown({ basePrice = 0, extras = 0, discountFactor = 1.0, quantity = 1 }) {
    const discountedBase = basePrice * discountFactor;
    const subtotal = discountedBase + extras;
    const final = subtotal * quantity;
    return {
        base: basePrice,
        extras,
        discountPct: Math.round((1 - discountFactor) * 100),
        subtotal,
        quantity,
        total: final,
    };
}

export function safeMany2One(value) {
    if (Array.isArray(value) && value.length === 2) return value;
    if (Array.isArray(value) && value.length === 1) return [value[0], ""];
    if (value && typeof value === "object" && "id" in value) return [value.id, value.display_name || ""];
    if (typeof value === "number") return [value, ""];
    return [false, ""];
}

export function validateProps(component, expectedProps) {
    for (const [key, def] of Object.entries(expectedProps)) {
        const value = component.props[key];
        const isOptional = typeof def === "object" && def.optional === true;
        const expectedType = typeof def === "string" ? def : def.type;
        if ((value === undefined || value === null)) {
            if (!isOptional) {
                console.warn(`[${component.constructor.name}] Missing required prop: "${key}"`);
            }
        } else if (expectedType && typeof value !== expectedType) {
            console.warn(`[${component.constructor.name}] Prop "${key}" expected to be ${expectedType}, got ${typeof value}`);
        }
    }
}

// Given a selected object and a list of ptalIds (attributes), ensures only one PTAV per attribute per bucket (left/right/shared)

export function dedupeSelected(selected, ptalIds) {
    // Only dedupe if someone selects a new value for the same attribute,
    // i.e. remove prior PTAVs for same attribute id
    // But since you have only ptavId as keys, you need to look up attr id by ptav id

    // Map ptavId => attrId for quick lookup
    const ptavIdToAttrId = {};
    ptalIds.forEach(attr => {
        (attr.values || []).forEach(val => {
            ptavIdToAttrId[val.id] = attr.id;
        });
    });

    // For a given bucket (left, right, shared)
    function dedupeBucket(bucket) {
        if (!bucket) return {};
        const attrToPtav = {}; // attrId => ptavId
        const deduped = {};
        for (const ptavIdStr in bucket) {
            const ptavId = Number(ptavIdStr);
            const attrId = ptavIdToAttrId[ptavId];
            // Always keep the most recent one (by order in bucket)
            if (attrToPtav[attrId]) {
                // Remove previous
                delete deduped[attrToPtav[attrId]];
            }
            deduped[ptavId] = bucket[ptavIdStr];
            attrToPtav[attrId] = ptavId;
        }
        return deduped;
    }

    const deduped = {};
    if (selected.shared) deduped.shared = dedupeBucket(selected.shared);
    if (selected.left) deduped.left = dedupeBucket(selected.left);
    if (selected.right) deduped.right = dedupeBucket(selected.right);
    return deduped;
}


export function isEmptySelected(sel) {
    if (!sel) return true;
    return (
        (!sel.left || Object.keys(sel.left).length === 0) &&
        (!sel.right || Object.keys(sel.right).length === 0) &&
        (!sel.shared || Object.keys(sel.shared).length === 0)
    );
}

// =============================
// FRONTEND HOOKS AND DEBOUNCERS
// =============================

export function useDebouncedInput(delay = 300) {
    let timeout = null;
    onWillUnmount(() => { if (timeout) clearTimeout(timeout); });
    return (callback) => {
        return (ev) => {
            const value = ev?.target?.value ?? ev;
            if (timeout) clearTimeout(timeout);
            timeout = setTimeout(() => { callback(value); }, delay);
        };
    };
}

export function debounce(func, wait = 300) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

export function nextTick() {
    return new Promise(resolve => setTimeout(resolve, 0));
}

// =============================
// BACKEND CLEANUP, GHOSTS, SAFE LOADS
// =============================

export async function waitForTargetRecord(targetResId, recordList, maxAttempts = 10, interval = 150) {
    let attempt = 0;
    while (attempt < maxAttempts) {
        const found = recordList.find((r) => r.resId === targetResId);
        if (found) {
            console.log(`Found target record after ${attempt + 1} attempt(s).`);
            return found;
        }
        console.log(`Attempt ${attempt + 1}: target record not found yet.`);
        attempt++;
        await new Promise(resolve => setTimeout(resolve, interval));
    }
    console.warn("Target record not found after maximum attempts.");
    return null;
}

export async function cleanGhostRecords(record, activeId) {
    if (!record?.model?.root?.data?.order_line) return;
    const orderLineData = record.model.root.data.order_line;
    const staleRecords = orderLineData.records?.filter(line => line.resId !== activeId) || [];
    if (staleRecords.length > 0) {
        console.log(`Cleaning ${staleRecords.length} ghost frontend records...`);
        orderLineData.records = orderLineData.records.filter(line => line.resId === activeId);
    } else {
        console.log("No ghost records found.");
    }
    if (typeof orderLineData.leaveEditMode === "function") {
        try { orderLineData.leaveEditMode(); } catch (error) { }
    }
    const orderRoot = record.model.root;
    if (orderRoot && "isDirty" in orderRoot) orderRoot.isDirty = false;
}

export async function afterSaveCleanup({ record, activeId, env, orderId }) {
    try {
        // Remove ghost/virtual lines from frontend
        if (record?.model?.root?.data?.order_line?.records) {
            record.model.root.data.order_line.records = record.model.root.data.order_line.records.filter(
                (line) => line.resId === activeId
            );
            record.model.root.data.order_line.leaveEditMode?.();
        }
        // UI pulse effect for saved line and total
        const lineEl = document.querySelector(`[data-id="${activeId}"]`);
        if (lineEl) {
            lineEl.scrollIntoView({ behavior: "smooth", block: "center" });
            lineEl.classList.add("highlight-success");
            setTimeout(() => lineEl.classList.remove("highlight-success"), 1500);
        }
        const totalEl = document.querySelector(".o_sale_order_total");
        if (totalEl) {
            totalEl.classList.add("highlight-success");
            setTimeout(() => totalEl.classList.remove("highlight-success"), 1500);
        }
        // Optional: redirect to sale order
        if (env?.services?.action && orderId) {
            await env.services.action.doAction({
                type: "ir.actions.act_window",
                res_model: "sale.order",
                res_id: orderId,
                views: [[false, "form"]],
                target: "current",
            });
        }
        if (env?.services?.notification) {
            env.services.notification.add("Order line updated!", { type: "success" });
        }
    } catch (err) {
        if (env?.services?.notification) {
            env.services.notification.add("Error during post-save cleanup.", { type: "danger" });
        }
        // Optionally: rethrow or log
        // throw err;
    }
}

 
// =============================
// CPQ ID/CONTEXT RESOLVERS
// =============================

export function resolvePartnerId(context = {}, env = {}) {
    let partnerIdRaw =
        context.partnerId || context.partner_id ||
        env?.services?.model?.root?.data?.partner_id?.[0];
    if (!partnerIdRaw && Array.isArray(env?.services?.model?.root?.data?.order_line?.records)) {
        const firstLine = env.services.model.root.data.order_line.records[0];
        const linePartner = firstLine?.data?.order_partner_id;
        if (Array.isArray(linePartner)) {
            partnerIdRaw = linePartner[0];
        }
    }
    const partnerId = typeof partnerIdRaw === "number"
        ? partnerIdRaw
        : parseInt(partnerIdRaw, 10);
    if (isNaN(partnerId)) {
        return null;
    }
    return partnerId;
}

export function resolveOrderId(context = {}, env = {}) {
    const root = env?.services?.model?.root;
    const fallbackId = root?.resId || root?.data?.id;
    return (
        context.orderId ||
        context.active_sale_order_id ||
        context.sale_order_id ||
        fallbackId ||
        null
    );
}

export function resolveSaleLineId(context = {}, env = {}) {
    const root = env?.services?.model?.root;
    const orderLines = root?.data?.order_line?.records;
    let activeId = context.active_id;
    if (!activeId && context.active_model === "sale.order" && Array.isArray(orderLines)) {
        activeId = orderLines[0]?.resId || null;
    }
    return activeId;
}

// =============================
// CPQ VISIBILITY, TRIGGERS, DEBUGGING
// =============================

export function getActiveTriggeredAttributeIds(selected, allAttributes) {
    const activeTriggers = new Set();
    const triggerSources = [];
    const flatSelected = {};
    if (selected?.left || selected?.right) {
        Object.assign(flatSelected, selected.left || {}, selected.right || {});
    } else {
        Object.assign(flatSelected, selected || {});
    }
    function walk(attributes) {
        for (const attr of attributes) {
            const values = attr.values || attr.ptav_ids || [];
            for (const val of values) {
                const isSelected = flatSelected?.[val.id] !== undefined;
                if (isSelected && Array.isArray(val.triggers)) {
                    for (const triggeredId of val.triggers) {
                        activeTriggers.add(triggeredId);
                        triggerSources.push({
                            sourceValue: `${val.name} (ID ${val.id})`,
                            sourceAttribute: `${attr.name} (ID ${attr.id})`,
                            triggers: triggeredId,
                        });
                    }
                }
            }
            if (attr.children?.length) walk(attr.children);
        }
    }
    walk(allAttributes);
    return activeTriggers;
}

function isTriggeredByAnything(targetAttrId, allAttrs) {
    let triggered = false;
    function walk(attrs) {
        for (const attr of attrs) {
            const values = attr.values || attr.ptav_ids || [];
            for (const val of values) {
                if (Array.isArray(val.triggers) && val.triggers.includes(targetAttrId)) {
                    triggered = true;
                    return;
                }
            }
            if (attr.children?.length) walk(attr.children);
        }
    }
    walk(allAttrs);
    return triggered;
}

export function filterVisibleAttributes(allAttributes, visibleAttrIds) {
    function recurse(attrList) {
        return attrList
            .map(attr => {
                if (attr.is_group) {
                    const visibleChildren = recurse(attr.children || []);
                    if (visibleChildren.length === 0) return null;
                    return { ...attr, children: visibleChildren };
                }
                const triggered = isTriggeredByAnything(attr.id, allAttributes);
                const isVisible = !triggered || visibleAttrIds.has(attr.id) || attr.required;
                return isVisible ? { ...attr, children: [] } : null;
            })
            .filter(Boolean);
    }
    return recurse(allAttributes);
}

export function getVisibleValueMap(attr, selected, allAttributes) {
    console.group(`[getVisibleValueMap] --- ${attr?.name || attr?.id || "unknown attribute"} ---`);
    // 1. Defensive: clone into plain object in case 'selected' is an OWL Proxy
    let _selected = selected;
    let cloneAttempted = false;
    try {
        _selected = JSON.parse(JSON.stringify(selected));
        cloneAttempted = true;
        console.log("[getVisibleValueMap] Successfully deep-cloned selected.");
    } catch (e) {
        console.warn("[getVisibleValueMap] Failed to deep-clone selected, using original object.", e);
    }
    console.log("[getVisibleValueMap] incoming selected:", selected);
    console.log("[getVisibleValueMap] _selected (clone):", _selected);
    console.log("[getVisibleValueMap] incoming selected keys:", Object.keys(selected || {}));
    if (cloneAttempted) {
        console.log("[getVisibleValueMap] cloned selected keys:", Object.keys(_selected || {}));
    }

    // 2. Flatten selection (shared, left/right, or plain)
    const flatSelected = {};
    if (_selected?.left || _selected?.right) {
        for (const [k, v] of Object.entries(_selected.left || {})) {
            flatSelected[String(k)] = v;
        }
        for (const [k, v] of Object.entries(_selected.right || {})) {
            flatSelected[String(k)] = v;
        }
    } else {
        for (const [k, v] of Object.entries(_selected || {})) {
            flatSelected[String(k)] = v;
        }
    }
    console.log("[getVisibleValueMap] flatSelected built:", flatSelected);
    console.log("[getVisibleValueMap] flatSelected keys:", Object.keys(flatSelected));

    // 3. Attribute trigger logic
    const isTriggered = allAttributes.some(parent =>
        (parent.values || []).some(val =>
            Array.isArray(val.triggers) && val.triggers.includes(attr.id)
        )
    );
    const hasActiveTrigger = allAttributes.some(parent =>
        (parent.values || []).some(
            val => (val.triggers || []).includes(attr.id) && flatSelected[String(val.id)] !== undefined
        )
    );
    const shouldShow = !isTriggered || hasActiveTrigger || attr.required;
    console.log(`[getVisibleValueMap] isTriggered:`, isTriggered, "hasActiveTrigger:", hasActiveTrigger, "shouldShow:", shouldShow);

    // 4. Map visible values
    const result = (attr.values || []).map(v => {
        // Use number IDs consistently
        const id = v.x_virtual_cpq_id ? Number(v.x_virtual_cpq_id) : Number(v.id);
        const selectedMeta = flatSelected[id] || {};

        // Extra debug per value
        const isValSelected = flatSelected.hasOwnProperty(id);
        if (isValSelected) {
            console.log(`[getVisibleValueMap] Value id=${id} (${v.name}) is selected, meta:`, selectedMeta);
        }

        return {
            ...v,
            idForSelection: id,
            visible: shouldShow,
            isPreferred: (
                v.isPreferred || selectedMeta.isPreferred ||
                v.isPreferredLeft || selectedMeta.isPreferredLeft ||
                v.isPreferredRight || selectedMeta.isPreferredRight ||
                false
            ),
            isPreferredLeft: v.isPreferredLeft || selectedMeta.isPreferredLeft || false,
            isPreferredRight: v.isPreferredRight || selectedMeta.isPreferredRight || false,
            note: v.note || selectedMeta.note || "",
        };
    });

    console.log("[getVisibleValueMap] result values:", result.map(r => ({
        id: r.id,
        name: r.name,
        visible: r.visible,
        isPreferred: r.isPreferred,
        isPreferredLeft: r.isPreferredLeft,
        isPreferredRight: r.isPreferredRight,
        note: r.note,
        idForSelection: r.idForSelection,
    })));
    console.groupEnd();
    return result;
}


export function findAttributeById(attributes, targetId) {
    for (const attr of attributes) {
        if (attr.id === targetId) return attr;
        if (attr.children?.length) {
            const found = findAttributeById(attr.children, targetId);
            if (found) return found;
        }
    }
    return null;
}

// =============================
// QR / PAYLOAD / MISCELLANEOUS
// =============================

export async function tryGenerateCpqQr(rpc, lineId, selector) {
    const el = typeof selector === "string" ? document.querySelector(selector) : selector;
    if (!lineId || !el) return;
    el.innerHTML = "";
    await generateCpqQrCanvasFromLineId(rpc, lineId, el);
}

export async function generateCpqQrCanvasFromLineId(rpc, lineId, containerElement) {
    if (!lineId || !containerElement) return;
    try {
        const response = await rpc("/cpq/qr_payload/" + lineId);
        const qrPayload = response?.qr_payload;
        if (!qrPayload) return;
        if (typeof QRCode === "undefined") return;
        new QRCode(containerElement, {
            text: qrPayload,
            width: 128,
            height: 128,
            colorDark: "#000000",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H,
        });
    } catch (error) {}
}

export async function generateQrDataUrl(rpc, lineId) {
    return new Promise(async (resolve) => {
        if (!lineId) return resolve(null);
        try {
            const response = await rpc("/cpq/qr_payload/" + lineId);
            const qrPayload = response?.qr_payload;
            if (!qrPayload) return resolve(null);
            if (typeof QRCode === "undefined") return resolve(null);
            const container = document.createElement("div");
            container.style.position = "absolute";
            container.style.left = "-9999px";
            document.body.appendChild(container);
            new QRCode(container, {
                text: qrPayload,
                width: 128,
                height: 128,
                colorDark: "#000000",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.H,
            });
            setTimeout(() => {
                try {
                    const canvas = container.querySelector("canvas");
                    if (!canvas) {
                        document.body.removeChild(container);
                        return resolve(null);
                    }
                    const dataUrl = canvas.toDataURL("image/png");
                    document.body.removeChild(container);
                    resolve(dataUrl);
                } catch (err) {
                    document.body.removeChild(container);
                    resolve(null);
                }
            }, 150);
        } catch (error) {
            resolve(null);
        }
    });
}

export function generateCpqOrderQrPayload(order) {
    if (!order || typeof order !== "object") return null;
    try {
        const payload = {
            type: "cpq_order",
            version: 1,
            order_id: order.id,
            customer: order.customer || "",
            date: order.date || new Date().toISOString().slice(0, 10),
            lines: (order.lines || []).map((line) => ({
                line_id: line.line_id,
                template_id: line.template_id,
                product_name: line.product_name || "",
                config_hash: line.config_hash || "",
                quantity: line.quantity || 1,
            })),
        };
        const json = JSON.stringify(payload);
        const base64 = btoa(json);
        return `cpq://order?data=${base64}`;
    } catch (err) {
        return null;
    }
}

export function parseCpqOrderQrPayload(qrString) {
    if (!qrString || typeof qrString !== "string") return null;
    try {
        const prefix = "cpq://order?data=";
        if (!qrString.startsWith(prefix)) return null;
        const base64Payload = qrString.slice(prefix.length);
        const jsonString = atob(base64Payload);
        const payload = JSON.parse(jsonString);
        if (payload?.type !== "cpq_order" || payload?.version !== 1) return null;
        return payload;
    } catch (err) {
        return null;
    }
}


export function getMergedSelected(effectiveSelected, mappedPrefs, configSplit) {
    const hasEffective = effectiveSelected && !isEmptySelected(effectiveSelected);
    const hasPrefs = mappedPrefs && Object.keys(mappedPrefs).length > 0;

    if (hasEffective) {
        return mergeSelectedWithFallback(effectiveSelected, mappedPrefs);
    }

    const emptyBuckets = { shared: {}, left: {}, right: {} };

    if (!hasPrefs) {
        // No selections and no preferences — return clean empty structure
        return emptyBuckets;
    }

    if (configSplit) {
        for (const ptavId of Object.keys(mappedPrefs)) {
            emptyBuckets.left[ptavId] = { ...mappedPrefs[ptavId] };
            emptyBuckets.right[ptavId] = { ...mappedPrefs[ptavId] };
        }
    } else {
        emptyBuckets.shared = { ...mappedPrefs };
    }

    return emptyBuckets;
}
