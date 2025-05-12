/** @odoo-module */

import { onWillUnmount } from "@odoo/owl";

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

export function useDebouncedInput(delay = 300) {
    let timeout = null;

    onWillUnmount(() => {
        if (timeout) clearTimeout(timeout);
    });

    return (callback) => {
        return (ev) => {
            const value = ev?.target?.value ?? ev;

            if (timeout) clearTimeout(timeout);
            timeout = setTimeout(() => {
                callback(value);
            }, delay);
        };
    };
}

export function debounce(func, wait = 300) {
    let timeout;
    return function (...args) {
        if (timeout) return;  
        timeout = setTimeout(() => {
            timeout = null;
        }, wait);
        return func.apply(this, args);
    };
}

export function nextTick() {
    return new Promise(resolve => setTimeout(resolve, 0));
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

export async function waitForTargetRecord(targetResId, recordList, maxAttempts = 10, interval = 150) {
    let attempt = 0;
    while (attempt < maxAttempts) {
        const found = recordList.find((r) => r.resId === targetResId);
        if (found) {
            console.log(`Found target record after ${attempt + 1} attempt(s).`);
            return found;
        }
        console.log(`⏳ Attempt ${attempt + 1}: target record not found yet.`);
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
        console.log(`🧹 Cleaning ${staleRecords.length} ghost frontend records...`);
        orderLineData.records = orderLineData.records.filter(line => line.resId === activeId);
    } else {
        console.log("No ghost records found.");
    }

    if (typeof orderLineData.leaveEditMode === "function") {
        try {
            orderLineData.leaveEditMode();
            console.log("Left edit mode cleanly.");
        } catch (error) {
            console.warn("leaveEditMode failed:", error);
        }
    }

    const orderRoot = record.model.root;
    if (orderRoot && "isDirty" in orderRoot) {
        orderRoot.isDirty = false;
        console.log("Cleared orderRoot isDirty flag.");
    }
}

export function getSafeConfiguratorValues(config, fallbackUomId) {
    const uomId = config.product_uom || fallbackUomId;
    if (!uomId) {
        console.warn("Missing Unit of Measure (UoM) in configurator result. Please check your dialog output.");
    }

    const quantity = config.quantity_to_make || 1;
    const priceUnit = config.price_unit || (config.total_price / quantity) || 0;

    // 🧹 Clean nested selected (avoid config.selected.selected)
    const selected = config?.selected?.selected || config.selected || {};
    
    if (config?.selected?.selected) {
        console.warn("⚠️ Detected nested selected in config. Flattening...");
    }
    
    const safeConfig = {
        ...config,
        selected,  // overwrite with flattened version
    };

    return {
        product_uom_qty: quantity,
        product_uom: uomId,
        price_unit: priceUnit,
        name: config.name || "Configured Product",
        cpq_configuration_json: JSON.stringify(safeConfig),
        cpq_configuration_summary: config.configuration_summary || "",
    };
}

export function safeMany2One(value) {
    if (Array.isArray(value) && value.length === 2) return value;  // Proper format
    if (Array.isArray(value) && value.length === 1) return [value[0], ""];  // Only ID, missing name
    if (value && typeof value === "object" && "id" in value) return [value.id, value.display_name || ""];
    if (typeof value === "number") return [value, ""];  // Number only
    return [false, ""];  // Safe fallback
}

export function getActiveTriggeredAttributeIds(selected, allAttributes) {
    const activeTriggers = new Set();
    let somethingSelected = false;

    function walk(attributes) {
        for (const attr of attributes) {
            if (attr.is_group && attr.children?.length) {
                walk(attr.children);
            } else if (attr.values?.length) {
                for (const val of attr.values) {
                    const isSelected = selected?.[val.id] !== undefined;
                    if (isSelected) {
                        somethingSelected = true;
                        for (const triggeredId of val.triggers || []) {
                            activeTriggers.add(triggeredId);
                        }
                    }
                }
            }
        }
    }

    walk(allAttributes);

    if (!somethingSelected) {
        // Show top-level non-triggered attributes
        const rootAttrIds = allAttributes.filter(a => !a.is_group).map(a => a.id);
        rootAttrIds.forEach(id => activeTriggers.add(id));
    }

    return activeTriggers;
}


export function filterVisibleAttributes(allAttributes, visibleAttrIds) {
    function recurse(attrList) {
        return attrList
            .map(attr => {
                const include = attr.is_group || visibleAttrIds.has(attr.id) || attr.required;
                if (!include) return null;
                return {
                    ...attr,
                    children: attr.children ? recurse(attr.children) : [],
                };
            })
            .filter(Boolean);
    }

    return recurse(allAttributes);
}

export function filterVisibleAttributeValues(attr, selected, allAttributes) {
    const triggeredBy = [];

    for (const parent of allAttributes) {
        for (const val of parent.values || []) {
            const triggers = val.triggers || [];
            if (triggers.includes(attr.id) && selected[val.id] !== undefined) {
                triggeredBy.push(val.id);
            }
        }
    }

    // 🔁 If the attribute is actively triggered → allow values
    if (triggeredBy.length > 0) {
        return attr.values || [];
    }

    // 🔁 If the attribute is *not* gated behind triggers → allow values
    const isTriggeredAttribute = allAttributes.some(attrCandidate =>
        attrCandidate.values?.some(v => (v.triggers || []).includes(attr.id))
    );

    if (!isTriggeredAttribute) {
        return attr.values || [];
    }

    // ❌ Else hide values (waiting for trigger)
    return [];
}


