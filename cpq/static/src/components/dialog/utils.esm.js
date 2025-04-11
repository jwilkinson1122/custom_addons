/** @odoo-module */

import { onWillUnmount } from "@odoo/owl";


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

// export function useDebouncedInput(delay = 300) {
//     let timeout;
//     return (callback) => (value) => {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => callback(value), delay);
//     };
// }

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
                console.warn(`⚠️ [${component.constructor.name}] Missing required prop: "${key}"`);
            }
        } else if (expectedType && typeof value !== expectedType) {
            console.warn(`⚠️ [${component.constructor.name}] Prop "${key}" expected to be ${expectedType}, got ${typeof value}`);
        }
    }
}

// export async function applyProduct(record, result) {
//     if (!record || !result) {
//         console.warn("⚠️ applyProduct: Missing record or result.");
//         return;
//     }

//     const changes = {};
//     const safeGet = (obj, path, fallback = null) => path.split('.').reduce((acc, key) => acc?.[key] ?? fallback, obj);

//     const config = result.configuration || {};
//     changes.name = config.name;
//     changes.cpq_configuration_json = config.cpq_configuration_json;
//     changes.cpq_configuration_summary = config.cpq_configuration_summary;

//     changes.product_uom_qty = config.quantity_to_make || 1;

//     try {
//         await record.update(changes);
//         console.log("✅ Record updated successfully:", changes);
//     } catch (error) {
//         console.error("❌ Failed to apply product config:", error);
//     }
// }

export async function applyProduct(record, configResult) {
    console.log("🧩 applyProduct() called with configResult:", configResult);

    if (!record) {
        console.warn("⚠️ No record provided to applyProduct.");
        return;
    }

    const config = configResult.configuration;
    if (!config) {
        console.warn("⚠️ No 'configuration' object found in result:", configResult);
        return;
    }

    const updates = {
        product_id: [configResult.product_id, configResult.product_display_name || config.name || "Configured Product"],
        cpq_configuration_json: config.cpq_configuration_json || "",
        cpq_configuration_summary: config.cpq_configuration_summary || "",
        product_uom_qty: config.quantity_to_make || 1,
    };

    console.log("💾 Updates prepared for record:", updates);

    try {
        await record.update(updates);
        console.log("✅ Order line after update:", record.data);

        record.model.root.data.order_line.leaveEditMode();

        console.log("✅ Order line updated with CPQ configuration.");
    } catch (error) {
        console.error("❌ Failed to update order line with configuration result:", error);
    }
}


