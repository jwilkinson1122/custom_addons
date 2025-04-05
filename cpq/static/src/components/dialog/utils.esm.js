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

export async function nextTick() {
    await Promise.resolve();                 // microtask
    await new Promise(r => setTimeout(r));   // full task (flushes Owl reactivity too)
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

        // Ensure UI refresh
        record.model.root.data.order_line.leaveEditMode();

        console.log("✅ Order line updated with CPQ configuration.");
    } catch (error) {
        console.error("❌ Failed to update order line with configuration result:", error);
    }
}


// export async function applyProduct(record, configResult) {
//     console.log("🧩 Applying configured product to order line:", configResult);

//     if (!record) {
//         console.warn("⚠️ No record provided to applyProduct.");
//         return;
//     }

//     const updates = {
//         product_id: [configResult.product_id, configResult.product_display_name],
//         cpq_configuration_json: configResult.configuration_json,
//         cpq_configuration_summary: configResult.configuration_summary,
//         product_uom_qty: configResult.configuration?.quantity_to_make || 1,
//     };

//     console.log("💾 Applying updates to record:", updates);

//     await record.update(updates);

//     record.model.root.data.order_line.leaveEditMode();

//     console.log("✅ Order line updated with CPQ configuration.");
// }



