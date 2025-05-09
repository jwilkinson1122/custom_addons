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

export function  getSafeConfiguratorValues(config, fallbackUomId) {
    const uomId = config.product_uom || fallbackUomId;
    if (!uomId) {
        console.warn("Missing Unit of Measure (UoM) in configurator result. Please check your dialog output.");
    }

    const quantity = config.quantity_to_make || 1;
    const priceUnit = config.price_unit || (config.total_price / quantity) || 0;

    return {
        product_uom_qty: quantity,
        product_uom: uomId,
        price_unit: priceUnit,
        name: config.name || "Configured Product",
        cpq_configuration_json: JSON.stringify(config),
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


