/** @odoo-module */

/** 
 * 🛠️ CPQ Utils Module
 * -------------------
 * Utility functions for CPQ configuration, QR generation, and scan workflows.
 *
 * 📌 Async / Await Guidance:
 * 
 * ✅ Asynchronous Functions (use async/await):
 * --------------------------------------------
 * - waitForTargetRecord              → Polls until target record found (uses await)
 * - waitForRealResIdFromRecord       → Waits for a valid resId (uses await)
 * - cleanGhostRecords                → May call async operations on records
 * - generateQrCanvas                 → Calls QR service (safe to treat as async)
 * - generateQrCodeInElement          → Calls generateQrCanvas (async)
 * - safeGenerateQrWithDebug          → Calls generateQrCanvas (async)
 * - startCpqQrScan                   → Uses camera stream + BarcodeDetector (async)
 * - sendCpqQrScanEvent               → RPC call via rpcService (async)
 * - scanCpqQrCode                    → RPC call via rpcService (async)
 * 
 * ❌ Synchronous Functions (do NOT use await):
 * --------------------------------------------
 * - computeLocalCPQPriceBreakdown    → Simple math calculation
 * - debounce                         → Timer-based debounce (pure sync)
 * - useDebouncedInput                → Sets up debounced input handler
 * - nextTick                         → Returns Promise.resolve() (correct use!)
 * - validateProps                    → Validates prop types (pure sync)
 * - getSafeConfiguratorValues        → Data preparation logic only
 * - safeMany2One                     → Handles Many2One values safely (pure)
 * - stableStringify                  → Recursively sorts keys and stringifies JSON
 * - generateCpqQrPayload             → Builds QR payload string
 * - renderCpqQrToElement             → Synchronous QR rendering (uses QRCode library)
 * - generateQrCodeUnified            → Combines payload generation + render (sync)
 *
 * ⚠️ REMINDER:
 * Do NOT await synchronous functions like `generateQrCodeUnified` or `renderCpqQrToElement`.
 * Use await ONLY on the listed async functions above.
 *
 * -------------------
 * © CPQ Customization for Odoo 17 — Maintained by [Your Team Name]
 */


import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";
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

export function useRpcService() {
    return useService('rpc');
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

export function useDebouncedInput(delay = 300) {
    let timeout = null;
    onWillUnmount(() => {
        if (timeout) clearTimeout(timeout);
    });
    return (callback) => (ev) => {
        const value = ev?.target?.value ?? ev;
        if (timeout) clearTimeout(timeout);
        timeout = setTimeout(() => callback(value), delay);
    };
}

export function pollQrWhenReady(getProps, el, interval = 300, maxAttempts = 20) {
    let attempts = 0;

    const checkAndGenerate = async () => {
        const props = getProps();

        const validLineId = props.lineId && typeof props.lineId === "number";
        const validOrderId = props.orderId && typeof props.orderId === "number";
        const validTemplateId = props.templateId && typeof props.templateId === "number";

        if (validOrderId && validLineId && validTemplateId) {
            console.log("✅ QR identifiers ready — generating QR code.");
            generateQrCodeUnified(props, el);
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

export async function waitForRealResIdFromRecord(record, maxAttempts = 20, interval = 150) {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        const resId = record?.resId;
        if (typeof resId === "number" && resId > 0) {
            console.log(`✅ Got real resId: ${resId} after ${attempt} attempt(s).`);
            return resId;
        }
        console.log(`⏳ Waiting for real resId (attempt ${attempt})...`, resId);
        await new Promise(resolve => setTimeout(resolve, interval));
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
    if (!config || typeof config !== "object") {
        console.error("❌ Invalid configuration object provided:", config);
        return {};
    }

    const uomId = config.product_uom || fallbackUomId || null;
    const safeUomId = Array.isArray(uomId) ? uomId[0] : uomId;

    if (!safeUomId) {
        console.warn("⚠️ Missing Unit of Measure (UoM) — fallback applied.");
    }

    const quantity = parseInt(config.quantity_to_make || config.product_uom_qty || 1, 10);
    const totalPrice = typeof config.total_price === "number" ? config.total_price : 0;
    // const priceUnit =
    //     typeof config.price_unit === "number"
    //         ? config.price_unit
    //         : totalPrice && quantity
    //         ? totalPrice / quantity
    //         : 0;

    const priceUnit =
    typeof config.price_unit === "number" && !isNaN(config.price_unit)
        ? config.price_unit
        : totalPrice && quantity
        ? totalPrice / quantity
        : 0;

    // Defensive string fallback for name and summary
    const name = typeof config.name === "string" ? config.name : "Configured Product";
    const summary =
        typeof config.configuration_summary === "string" ? config.configuration_summary : "";

    const laterality = ["left", "right", "bilateral"].includes(config.laterality)
        ? config.laterality
        : null;

    const result = {
        product_uom_qty: quantity,
        product_uom: safeUomId || null,
        price_unit: priceUnit,
        name: name,
        cpq_configuration_json: JSON.stringify(config),
        cpq_configuration_summary: summary,
        cpq_laterality: laterality,
        cpq_quantity_to_make: quantity,
    };

    console.debug("🟢 Prepared safe configurator values:", result);
    return result;
}

export function safeMany2One(value) {
    if (Array.isArray(value) && value.length === 2) return value;  // Proper format
    if (Array.isArray(value) && value.length === 1) return [value[0], ""];  // Only ID, missing name
    if (value && typeof value === "object" && "id" in value) return [value.id, value.display_name || ""];
    if (typeof value === "number") return [value, ""];  // Number only
    return [false, ""];  // Safe fallback
}

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
    let uri = `cpq://order/${orderId}`;
    if (lineId) uri += `/line/${lineId}`;
    uri += `/template/${templateId}`;
    const params = [`v=${version}`];
    if (configHash) params.push(`config=${encodeURIComponent(configHash)}`);
    return `${uri}?${params.join("&")}`;
}

export function renderCpqQrToElement(payload, targetElement, debug = false) {
    if (!targetElement) {
        console.warn("⚠️ No target element provided for QR generation.");
        return;
    }
    targetElement.innerHTML = "";  // Clear previous QR
    if (debug) console.log("🟢 Generating QR with payload:", payload);
    new QRCode(targetElement, {
        text: payload,
        width: 128,
        height: 128,
        correctLevel: QRCode.CorrectLevel.H,
    });
}

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
        const canvas = el.querySelector('.cpq-order-line-qr-canvas');
        if (canvas) {
            generateQrCanvas(payload, canvas);
        }
    }
};

export async function safeGenerateQrWithDebug(payload, el, debug = false) {
    if (!payload) {
        console.error("❌ QR Generation skipped: Missing payload.");
        return;
    }

    const canvas = el.querySelector('.cpq-order-line-qr-canvas');
    if (!canvas) {
        console.warn("⚠️ QR Generation skipped: .cpq-order-line-qr-canvas element not found.");
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

export function generateQrCodeUnified(identifiers, el, debug = false) {
    const payload = generateCpqQrPayload(identifiers);
    renderCpqQrToElement(payload, el, debug);
}

export async function startCpqQrScan(onScanResult) {
    const video = document.createElement("video");
    const stream = await browser.navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
    video.srcObject = stream;
    await video.play();

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const detector = new window.BarcodeDetector({ formats: ["qr_code"] });

    const scanLoop = async () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        try {
            const detections = await detector.detect(canvas);
            if (detections.length) {
                stream.getTracks().forEach(track => track.stop());
                onScanResult(detections[0].rawValue);
            } else {
                requestAnimationFrame(scanLoop);
            }
        } catch (error) {
            console.error("QR scan error:", error);
            requestAnimationFrame(scanLoop);
        }
    };
    scanLoop();
}

export async function sendCpqQrScanEvent(payload, status = "scan-in") {
    const rpcService = useService('rpc');
    try {
        const response = await rpcService("/cpq/qr_scan", { payload, status });
        console.log("✅ Scan event submitted successfully:", response);
        return response;
    } catch (error) {
        console.error("❌ Failed to send scan event:", error);
        throw error;
    }
}

export async function scanCpqQrCode(rpcService, qrPayload) {
    try {
        const response = await rpcService("/cpq/scan_qr", {
            qr_data: qrPayload,
        });
        if (response.error) {
            console.warn("⚠️ CPQ QR Scan error:", response.error);
            return { success: false, message: response.error };
        }
        console.log("✅ CPQ QR Scan result:", response);
        return { success: true, data: response };
    } catch (error) {
        console.error("❌ CPQ QR Scan failed:", error);
        return { success: false, message: "Failed to process QR scan." };
    }
}



