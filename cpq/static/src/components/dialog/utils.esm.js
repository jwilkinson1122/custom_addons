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

export function findAttributeById(attributes, targetId) {
    for (const attr of attributes) {
        if (attr.id === targetId) {
            console.log(`✅ Found attribute ID ${targetId}:`, attr.name);
            return attr;
        }
        if (attr.children?.length) {
            const found = findAttributeById(attr.children, targetId);
            if (found) {
                console.log(`🔎 Found nested attribute ID ${targetId} under group ${attr.name}`);
                return found;
            }
        }
    }
    console.warn(`❌ Attribute ID ${targetId} not found in attribute tree`);
    return null;
}

export function getActiveTriggeredAttributeIds(selected, allAttributes) {
    const activeTriggers = new Set();
    const triggerSources = [];

    // 🔄 Normalize to flat selection
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

            if (attr.children?.length) {
                walk(attr.children);
            }
        }
    }

    walk(allAttributes);

    if (triggerSources.length) {
        console.group("🔁 Triggered Attributes:");
        triggerSources.forEach(t =>
            console.log(`✅ "${t.sourceValue}" from "${t.sourceAttribute}" triggers attribute ID ${t.triggers}`)
        );
        console.groupEnd();
    } else {
        console.warn("⚠️ No triggers were activated.");
    }

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
                if (attr.is_group || attr.required) {
                    return { ...attr, children: recurse(attr.children || []) };
                }

                const triggered = isTriggeredByAnything(attr.id, allAttributes);
                if (!triggered || visibleAttrIds.has(attr.id)) {
                    return { ...attr, children: recurse(attr.children || []) };
                }

                return null;
            })
            .filter(Boolean);
    }

    return recurse(allAttributes);
}

 
export function filterVisibleAttributeValues(attr, selected, allAttributes) {
    const flatSelected = {};
    if (selected?.left || selected?.right) {
        Object.assign(flatSelected, selected.left || {}, selected.right || {});
    } else {
        Object.assign(flatSelected, selected || {});
    }

    const isTriggeredByAnything = allAttributes.some(parent =>
        (parent.values || []).some(val => Array.isArray(val.triggers) && val.triggers.includes(attr.id))
    );

    if (!isTriggeredByAnything) return attr.values || [];

    const hasTriggerActive = allAttributes.some(parent =>
        (parent.values || []).some(
            val => (val.triggers || []).includes(attr.id) && flatSelected[val.id] !== undefined
        )
    );

    if (hasTriggerActive || attr.required) return attr.values || [];

    return [];
}

export function getVisibleValueMap(attr, selected, allAttributes) {
    const flatSelected = {};
    if (selected?.left || selected?.right) {
        Object.assign(flatSelected, selected.left || {}, selected.right || {});
    } else {
        Object.assign(flatSelected, selected || {});
    }

    const isTriggered = allAttributes.some(parent =>
        (parent.values || []).some(val => Array.isArray(val.triggers) && val.triggers.includes(attr.id))
    );

    const hasActiveTrigger = allAttributes.some(parent =>
        (parent.values || []).some(
            val => (val.triggers || []).includes(attr.id) && flatSelected[val.id] !== undefined
        )
    );

    const shouldShow = !isTriggered || hasActiveTrigger || attr.required;

    return (attr.values || []).map(v => ({ ...v, visible: shouldShow }));
}

export function debugVisibleAttributes(allAttributes, visibleAttributeIds) {
    const all = new Set();
    const visible = new Set(visibleAttributeIds);

    function walk(attrs) {
        for (const attr of attrs) {
            all.add(attr.id);
            if (attr.children?.length) walk(attr.children);
        }
    }

    walk(allAttributes);

    const hidden = [...all].filter((id) => !visible.has(id));
    if (hidden.length > 0) {
        console.warn("🚫 Hidden attribute IDs (not triggered):", hidden);
    } else {
        console.log("✅ All attributes are currently visible.");
    }
}


