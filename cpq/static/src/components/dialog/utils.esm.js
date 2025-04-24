/** @odoo-module */
import { registry } from "@web/core/registry";
import { onWillUnmount } from "@odoo/owl";
// import QRCode from 'qrcode';
// import QRCode from 'web.qrcode';


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

// let qrGenerationTimeout = null;

// export function debounceQrWhenReady(getProps, el, delay = 300) {
//     if (qrGenerationTimeout) clearTimeout(qrGenerationTimeout);

//     qrGenerationTimeout = setTimeout(() => {
//         const props = getProps();

//         const validLineId = props.lineId && typeof props.lineId === "number";
//         const validOrderId = props.orderId && typeof props.orderId === "number";
//         const validTemplateId = props.templateId && typeof props.templateId === "number";

//         if (validOrderId && validLineId && validTemplateId) {
//             generateQrCodeUnified(props, el);
//         } else {
//             console.warn("⚠️ Skipping debounced QR generation — missing valid identifiers:", {
//                 orderId: props.orderId,
//                 lineId: props.lineId,
//                 templateId: props.templateId,
//             });
//         }
//     }, delay);
// }

/**
 * Polls for valid QR identifiers (orderId, lineId, templateId) and generates QR when ready.
 * Stops automatically after success.
 * 
 * @param {Function} getProps - Function returning current props.
 * @param {HTMLElement} el - Element where the QR should be generated.
 * @param {number} interval - Polling interval in ms (default 300).
 * @param {number} maxAttempts - Maximum attempts before giving up (default 20).
 */
export function pollQrWhenReady(getProps, el, interval = 300, maxAttempts = 20) {
    let attempts = 0;

    const checkAndGenerate = async () => {
        const props = getProps();

        const validLineId = props.lineId && typeof props.lineId === "number";
        const validOrderId = props.orderId && typeof props.orderId === "number";
        const validTemplateId = props.templateId && typeof props.templateId === "number";

        if (validOrderId && validLineId && validTemplateId) {
            console.log("✅ QR identifiers ready — generating QR code.");
            await generateQrCodeUnified(props, el);
        } else if (attempts < maxAttempts) {
            attempts++;
            setTimeout(checkAndGenerate, interval);
        } else {
            console.warn(`❌ QR generation skipped after ${attempts} attempts — still missing identifiers:`, {
                orderId: props.orderId,
                lineId: props.lineId,
                templateId: props.templateId,
            });
        }
    };

    checkAndGenerate();
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

export async function waitForTargetRecord(targetResId, recordList, maxAttempts = 10, interval = 150) {
    let attempt = 0;
    while (attempt < maxAttempts) {
        const found = recordList.find((r) => r.resId === targetResId);
        if (found) {
            console.log(`✅ Found target record after ${attempt + 1} attempt(s).`);
            return found;
        }
        console.log(`⏳ Attempt ${attempt + 1}: target record not found yet.`);
        attempt++;
        await new Promise(resolve => setTimeout(resolve, interval));
    }
    console.warn("⚠️ Target record not found after maximum attempts.");
    return null;
}

/**
 * Waits for a single record's `resId` to become a valid number.
 * @param {Object} record - The record object (not a list).
 * @param {number} maxAttempts - Max retries.
 * @param {number} interval - Delay between attempts (ms).
 * @returns {Promise<number|null>} - The resId if found, or null.
 */
export async function waitForRealResIdFromRecord(record, maxAttempts = 20, interval = 150) {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        const resId = record?.resId;
        if (typeof resId === "number" && resId > 0) {
            console.log(`✅ Got real resId: ${resId} after ${attempt} attempt(s).`);
            return resId;
        }
        console.log(`⏳ Waiting for real resId (attempt ${attempt})...`, resId);
        await new Promise((resolve) => setTimeout(resolve, interval));
    }
    console.warn("❌ Failed to get a real resId after maximum attempts.");
    return null;
}


export async function cleanGhostRecords(record, lineId) {
    if (!record?.model?.root?.data?.order_line) return;

    const orderLineData = record.model.root.data.order_line;
    const staleRecords = orderLineData.records?.filter(line => line.resId !== lineId) || [];

    if (staleRecords.length > 0) {
        console.log(`🧹 Cleaning ${staleRecords.length} ghost frontend records...`);
        orderLineData.records = orderLineData.records.filter(line => line.resId === lineId);
    } else {
        console.log("✅ No ghost records found.");
    }

    if (typeof orderLineData.leaveEditMode === "function") {
        try {
            orderLineData.leaveEditMode();
            console.log("✅ Left edit mode cleanly.");
        } catch (error) {
            console.warn("⚠️ leaveEditMode failed:", error);
        }
    }

    const orderRoot = record.model.root;
    if (orderRoot && "isDirty" in orderRoot) {
        orderRoot.isDirty = false;
        console.log("✅ Cleared orderRoot isDirty flag.");
    }
}

export function getSafeConfiguratorValues(config, fallbackUomId) {
    const uomId = config.product_uom || fallbackUomId;
    const safeUomId = Array.isArray(uomId) ? uomId[0] : uomId;

    if (!safeUomId) {
        console.warn("⚠️ Missing Unit of Measure (UoM) — fallback applied.");
    }

    const quantity = config.quantity_to_make || 1;
    const priceUnit = config.price_unit || (config.total_price / quantity) || 0;

    return {
        product_uom_qty: quantity,
        product_uom: safeUomId || null,  // ✅ Never false — either number or null
        price_unit: priceUnit,
        name: config.name || "Configured Product",
        cpq_configuration_json: JSON.stringify(config),
        cpq_configuration_summary: config.configuration_summary || "",
    };
}


// export function  getSafeConfiguratorValues(config, fallbackUomId) {
//     const uomId = config.product_uom || fallbackUomId;
//     if (!uomId) {
//         console.warn("⚠️ Missing Unit of Measure (UoM) in configurator result. Please check your dialog output.");
//     }

//     const quantity = config.quantity_to_make || 1;
//     const priceUnit = config.price_unit || (config.total_price / quantity) || 0;

//     return {
//         product_uom_qty: quantity,
//         product_uom: uomId,
//         price_unit: priceUnit,
//         name: config.name || "Configured Product",
//         cpq_configuration_json: JSON.stringify(config),
//         cpq_configuration_summary: config.configuration_summary || "",
//     };
// }

export function safeMany2One(value) {
    if (Array.isArray(value) && value.length === 2) return value;  // Proper format
    if (Array.isArray(value) && value.length === 1) return [value[0], ""];  // Only ID, missing name
    if (value && typeof value === "object" && "id" in value) return [value.id, value.display_name || ""];
    if (typeof value === "number") return [value, ""];  // Number only
    return [false, ""];  // Safe fallback
}

/**
 * Recursively sorts keys of an object for consistent JSON output.
 */
export function stableStringify(obj) {
    const sortKeys = (input) => {
        if (Array.isArray(input)) {
            return input.map(sortKeys);
        } else if (input && typeof input === "object" && input.constructor === Object) {
            return Object.keys(input).sort().reduce((acc, key) => {
                acc[key] = sortKeys(input[key]);
                return acc;
            }, {});
        }
        return input;
    };
    return JSON.stringify(sortKeys(obj));
}



export function generateCpqQrPayload({ orderId, lineId, templateId, configHash = null, version = 1 }) {
    let uri = `cpq://order/${orderId}/line/${lineId}/template/${templateId}`;
    const params = [];
    if (configHash) params.push(`config=${encodeURIComponent(configHash)}`);
    if (version) params.push(`v=${version}`);
    if (params.length) uri += `?${params.join("&")}`;
    return uri;
}

/**
 * Generates a QR Code directly onto a canvas element.
 * @param {string} payload - The QR URI payload string.
 * @param {HTMLCanvasElement} canvasElement - The target canvas element.
 */
export async function generateQrCanvas(payload, canvasElement) {
    if (!canvasElement) {
        console.warn("⚠️ Missing canvas element for QR code generation.");
        return;
    }

    const qrService = registry.category("services").get("qr_code");
    if (!qrService || !qrService.makeQR) {
        console.error("❌ QR code service not found.");
        return;
    }

    // Clear the canvas or container first
    canvasElement.innerHTML = ""; // Needed if using divs/SVG

    try {
        qrService.makeQR(canvasElement, payload);  // This will auto-render into the element.
    } catch (err) {
        console.error("❌ Failed to generate QR Code via Odoo QR service:", err);
    }
}

export async function generateQrCodeInElement(props, el) {
    if (props.orderId && props.lineId && props.templateId) {
        const payload = generateCpqQrPayload({
            orderId: props.orderId,
            lineId: props.lineId,
            templateId: props.templateId,
            configHash: props.configHash || null,
        });
        const canvas = el.querySelector('.cpq-qr-canvas');
        if (canvas) {
            generateQrCanvas(payload, canvas);
        }
    }
};

/**
 * Safely generates a QR code with debug logging.
 * @param {string} payload - The QR code payload (URI-style string).
 * @param {HTMLElement} el - The parent element to search for the QR canvas.
 * @param {boolean} [debug=false] - Enable verbose logging.
 */
export async function safeGenerateQrWithDebug(payload, el, debug = false) {
    if (!payload) {
        console.error("❌ QR Generation skipped: Missing payload.");
        return;
    }

    const canvas = el.querySelector('.cpq-qr-canvas');
    if (!canvas) {
        console.warn("⚠️ QR Generation skipped: .cpq-qr-canvas element not found.");
        return;
    }

    if (debug) {
        console.log("🟢 Generating QR with payload:", payload);
        console.log("🟢 Canvas found:", !!canvas);
    }

    try {
        await generateQrCanvas(payload, canvas);
        if (debug) {
            console.log("✅ QR Code successfully rendered to canvas.");
        }
    } catch (err) {
        console.error("❌ Failed to generate QR Code on canvas:", err);
    }
}

/**
 * Unified QR generation with optional debug logging.
 * @param {Object} props - Props object including orderId, lineId, templateId, configHash.
 * @param {HTMLElement} el - The DOM element where the QR code canvas lives.
 * @param {boolean} debug - Whether to log debug info (default: false).
 */
export async function generateQrCodeUnified(props, el, debug = false) {
    if (props.orderId && props.lineId && props.templateId) {
        const payload = generateCpqQrPayload({
            orderId: props.orderId,
            lineId: props.lineId,
            templateId: props.templateId,
            configHash: props.configHash || null,
        });

        const canvas = el.querySelector('.cpq-qr-canvas');
        if (debug) {
            console.log("🟢 QR Payload:", payload);
            console.log("🟢 Canvas found:", !!canvas);
        }

        if (canvas) {
            await generateQrCanvas(payload, canvas);
        } else if (debug) {
            console.warn("⚠️ QR Canvas not found — skipping QR generation.");
        }
    } else if (debug) {
        console.warn("❌ Missing one or more identifiers (orderId, lineId, templateId) — QR not generated.");
    }
}


