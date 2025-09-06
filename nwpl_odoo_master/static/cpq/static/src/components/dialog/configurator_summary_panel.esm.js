/** @odoo-module **/
import { useService } from "@web/core/utils/hooks";
import { Component, useState, useRef, onMounted, onWillUpdateProps, onWillUnmount, html } from "@odoo/owl";
import { debounce, generateCpqQrCanvasFromLineId, generateQrDataUrl, tryGenerateCpqQr } from "./utils.esm";

function formatCurrency(amount) {
    const number = typeof amount === "number" ? amount : parseFloat(amount) || 0;
    return `$${number.toFixed(2)}`;
}

function cleanValue(val) {
    return (typeof val === "string" && val.trim()) ? val.trim() : "-";
}

// Helper to flatten {attrId: {ptavId: valueObj}} to {ptavId: valueObj}
function flattenSelectedBucket(bucket) {
    if (!bucket) return {};
    // If already flat: all values have an 'id' (valueObj) or are primitives
    if (Object.values(bucket).every(v =>
        v && typeof v === "object" && "id" in v || typeof v !== "object"
    )) {
        return bucket;
    }
    // Otherwise, flatten nested {attrId: {ptavId: valueObj}}
    const flat = {};
    for (const sub of Object.values(bucket)) {
        if (sub && typeof sub === "object") {
            for (const [ptavId, valObj] of Object.entries(sub)) {
                flat[ptavId] = valObj;
            }
        }
    }
    return flat;
}


// --- "Fan out shared" helper ---
// This ensures that in non-split bilateral mode, left/right appear as shared.

// function getEffectiveSelectedBuckets(selected, split, laterality) {
//     let left = selected.left || {};
//     let right = selected.right || {};
//     let shared = selected.shared || {};
//     if (!split && laterality === "bilateral" && Object.keys(shared).length > 0) {
//         left = shared;
//         right = shared;
//     }
//     return { left, right, shared };
// }

function getEffectiveSelectedBuckets(selected, split, laterality) {
    let left = selected.left || {};
    let right = selected.right || {};
    const shared = selected.shared || {};

    if (laterality === "bilateral" && !split && Object.keys(shared).length > 0) {
        // Bilateral shared
        left = shared;
        right = shared;
    } else if (laterality === "left" && Object.keys(left).length === 0 && Object.keys(shared).length > 0) {
        // Left-only → fan out shared
        left = shared;
    } else if (laterality === "right" && Object.keys(right).length === 0 && Object.keys(shared).length > 0) {
        // Right-only → fan out shared
        right = shared;
    }

    return { left, right, shared };
}

export default class ConfiguratorSummaryPanel extends Component {
    setup() {
        super.setup();

        const props = this.props;
        this.lineId = props.record?.resId || props.lineId || null;
        this.productTemplate = props.productTemplate;
        this.formatCurrency = formatCurrency;
        this.summaryWrapper = useRef("summaryWrapper");
        this.qrCanvasRef = useRef("qrCanvasRef");
        this.rpc = useService("rpc");
        this.toastQueue = [];
        this.cleanValue = cleanValue;
        this.state = useState({
            summary: [],
            priceSummary: {
                left: 0,
                right: 0,
                shared: 0,
                base: 0,
                total: 0,
                extrasSubtotal: 0,
            },
            expanded: false,
            height: 0,
            showExtras: true,
            quantityToMake: props.quantityToMake || 1,
            toastMessage: "",
        });

        // Log here
        console.log("[ConfiguratorSummaryPanel.setup] Initial props.selected:", JSON.stringify(this.props.selected, null, 2));
        console.log("[ConfiguratorSummaryPanel.setup] Initial props.ptalIds:", JSON.stringify(this.props.ptalIds, null, 2));
        // Add any other props you care about for debugging

        this.realLineId = useState({ value: null });

        this._registerExternalApi();

        const debouncedRecomputeSummary = debounce(() => {
            console.log("Debounced recompute summary");
            requestAnimationFrame(() => {
                this._preserveScroll(() => this.computeSummary());
            });
        }, 150);

        const debouncedAdjustHeight = debounce(() => {
            console.log("Debounced adjustHeight");
            this.adjustHeight();
        }, 150);

        onMounted(async () => {
            console.log("SummaryPanel mounted");

            const tryRenderQr = async () => {
                for (let i = 0; i < 10; i++) {
                    const el = document.querySelector("#cpq-canonical-qr");
                    if (this.lineId && el) {
                        await tryGenerateCpqQr(this.rpc, this.lineId, el);
                        break;
                    }
                    await new Promise(resolve => setTimeout(resolve, 300));
                }
            };
            tryRenderQr();
            
            if (props.ptalIds?.length > 0) {
                console.log("Initial ptalIds detected, computing summary...");
                this.computeSummary();
            }

            this.adjustHeight();

        });

        onWillUpdateProps((nextProps) => {

            if (!this.props.lineId && nextProps.lineId && this.qrCanvasRef?.el) {
                console.log("Detected new lineId — generating QR:", nextProps.lineId);
                tryGenerateCpqQr(this.rpc, nextProps.lineId, this.qrCanvasRef.el);
            }

            let needsRecompute = false;
            let needsHeightAdjust = false;

            if (nextProps.quantityToMake !== this.state.quantityToMake) {
                console.log("Quantity changed:", nextProps.quantityToMake);
                this.state.quantityToMake = nextProps.quantityToMake;
                needsRecompute = true;
                needsHeightAdjust = true;
            }

            if (nextProps.laterality !== props.laterality) {
                console.log("Laterality changed:", nextProps.laterality);
                props.laterality = nextProps.laterality;
                needsRecompute = true;
                needsHeightAdjust = true;
            }

            if (nextProps.split !== props.split) {
                console.log("Split mode changed:", nextProps.split);
                props.split = nextProps.split;
                needsRecompute = true;
                needsHeightAdjust = true;
            }

            if (nextProps.selected !== props.selected) {
                console.log("Selected attributes changed.");
                props.selected = nextProps.selected;
                needsRecompute = true;
            }

            if (nextProps.ptalIds !== props.ptalIds) {
                console.log("PTAL IDs changed (attribute structure).");
                props.ptalIds = nextProps.ptalIds;
                needsRecompute = true;
                needsHeightAdjust = true;
            }

            if (JSON.stringify(nextProps.splitByAttrMap) !== JSON.stringify(props.splitByAttrMap)) {
                console.log("SplitByAttrMap changed.");
                props.splitByAttrMap = nextProps.splitByAttrMap;
                needsRecompute = true;
            }


            if (needsRecompute) debouncedRecomputeSummary();
            if (needsHeightAdjust) debouncedAdjustHeight();
        });

        onWillUnmount(() => {
            clearTimeout(this._heightTimeout);
            clearTimeout(this._toastTimeout);
            this.toastQueue = [];
        });

        this.computeSummary();
        console.log("Initial computeSummary:", this.state.quantityToMake);
    }

    _registerExternalApi() {
        if (this.props.register) {
            this.props.register({
                showToast: (msg) => this.showToast(msg),
                getSummaryState: () => ({
                    selections: this.state.summary,
                    priceSummary: this.state.priceSummary,
                    left: this.state.priceSummary.left,
                    right: this.state.priceSummary.right,
                    total: this.state.priceSummary.total,
                }),
                getLeftTotal: () => this.state.priceSummary.left,
                getRightTotal: () => this.state.priceSummary.right,
                getCombinedTotal: () => this.state.priceSummary.total,
                refreshQr: () => {
                    if (this.props.lineId && this.qrCanvasRef?.el) {
                        tryGenerateCpqQr(this.rpc, this.props.lineId, this.qrCanvasRef.el);
                    }
                },
            });
        }
    }

    adjustHeight() {
        clearTimeout(this._heightTimeout);
        this._heightTimeout = setTimeout(() => {
            const wrapper = this.summaryWrapper?.el;
            if (!wrapper) return;

            const table = wrapper.querySelector("table");
            if (!table) return;

            // const targetHeight = table.offsetHeight + 16; 
            const targetHeight = table.scrollHeight + 16;
            if (this.state.height !== targetHeight) {
                console.log(`Adjusting summary height: ${targetHeight}px`);
                this.state.height = targetHeight;
            }
        }, 50);
    }

    showToast(message) {
        this.toastQueue.push(message);
        if (this._toastTimeout) return;

        const showNextToast = () => {
            if (!this.toastQueue.length) {
                this._toastTimeout = null;
                return;
            }
            this.state.toastMessage = this.toastQueue.shift();
            this._toastTimeout = setTimeout(() => {
                this.state.toastMessage = "";
                showNextToast();
            }, 2000);
        };

        showNextToast();
    }

    toggleExpand() {
        this.state.expanded = !this.state.expanded;
        this.adjustHeight();
    }

    _preserveScroll(fn) {
        const scrollY = this.summaryWrapper?.el?.scrollTop || 0;
        fn();
        setTimeout(() => {
            if (this.summaryWrapper?.el) {
                this.summaryWrapper.el.scrollTop = scrollY;
            }
        }, 0);
    }

    // ----------- MAIN SUMMARY COMPUTATION (with shared logic) -----------
    // computeSummary() {
    //     const {
    //         ptalIds = [],
    //         selected = {},
    //         laterality,
    //         split,
    //         splitByAttrMap = {},
    //         productTemplate,
    //         quantityToMake = 1,
    //     } = this.props;

    //     const { left: selectedLeft, right: selectedRight, shared: selectedShared } = getEffectiveSelectedBuckets(selected, split, laterality);

    //     let leftTotal = 0;
    //     let rightTotal = 0;

    //     const flattenAttributes = (tree) => {
    //         const flat = [];
    //         const recurse = (nodes) => {
    //             for (const node of nodes) {
    //                 if (node.is_group && node.children) {
    //                     recurse(node.children);
    //                 } else {
    //                     flat.push(node);
    //                 }
    //             }
    //         };
    //         recurse(tree);
    //         return flat;
    //     };
    //     const allAttributes = flattenAttributes(ptalIds);

    //     const getSelectedValue = (values, dict) => {
    //         for (const v of values) {
    //             const key1 = v.x_virtual_cpq_id !== undefined ? String(v.x_virtual_cpq_id) : null;
    //             const key2 = String(v.id);
    //             if (key1 && dict.hasOwnProperty(key1)) {
    //                 const val = dict[key1];
    //                 return { ...v, ...(typeof val === "object" ? val : { value: val }) };
    //             }
    //             if (dict.hasOwnProperty(key2)) {
    //                 const val = dict[key2];
    //                 return { ...v, ...(typeof val === "object" ? val : { value: val }) };
    //             }
    //         }
    //         return null;
    //     };

    //     const formatValue = (val) => {
    //         if (!val) return "-";
    //         return val.is_custom && val.value ? `✍️ ${val.value}` : val.name || "-";
    //     };

    //     console.log("[SUMMARY] ptalIds", allAttributes.map(a => [a.id, a.name]));
    //     console.log("[SUMMARY] splitByAttrMap", splitByAttrMap);
    //     console.log("[SUMMARY] selected.left", selectedLeft);
    //     console.log("[SUMMARY] selected.right", selectedRight);
    //     console.log("[SUMMARY] selected.shared", selectedShared);

    //     const result = allAttributes.map((attr) => {

    //         const values = attr.values || [];
    //         if (!attr.name || values.length === 0) return null;

    //         const isSplitForAttr = laterality === "bilateral" && (splitByAttrMap[String(attr.id)] || split);
    //         console.log('splitByAttrMap actual object:', JSON.stringify(splitByAttrMap));
    //         console.log("splitByAttrMap keys:", Object.keys(splitByAttrMap));
    //         console.log("attr.id:", attr.id, typeof attr.id);
    //         console.log(
    //         `[SUMMARY ROW] attr.id=${attr.id} isSplitForAttr=${isSplitForAttr}`,
    //         { selectedLeft, selectedRight, selectedShared, values }
    //         );

    //         let leftVal = null, rightVal = null, sharedVal = null;
    //         let left = "-", right = "-", shared = "-";
    //         let match = false, priceExtra = 0;

    //         let isPreferredLeft = false, isPreferredRight = false, isPreferredShared = false;

    //         if (isSplitForAttr) {
    //             leftVal = getSelectedValue(values, selectedLeft);
    //             rightVal = getSelectedValue(values, selectedRight);
    //             if (!leftVal && Object.keys(selectedShared).length)
    //                 leftVal = getSelectedValue(values, selectedShared);
    //             if (!rightVal && Object.keys(selectedShared).length)
    //                 rightVal = getSelectedValue(values, selectedShared);

    //             console.log(`[SUMMARY VALS] ${attr.name} leftVal=`, leftVal, 'rightVal=', rightVal, 'sharedVal=', sharedVal);

    //             if (!leftVal && !rightVal) {
    //                 return null;
    //             }

    //             left = formatValue(leftVal);
    //             right = formatValue(rightVal);

    //             isPreferredLeft = !!(leftVal?.isPreferredLeft ?? leftVal?.isPreferred ?? false);
    //             isPreferredRight = !!(rightVal?.isPreferredRight ?? rightVal?.isPreferred ?? false);

    //             const leftExtra = (leftVal?.price_extra || 0) * quantityToMake;
    //             const rightExtra = (rightVal?.price_extra || 0) * quantityToMake;
    //             leftTotal += leftExtra;
    //             rightTotal += rightExtra;
    //             priceExtra = leftExtra + rightExtra;
    //             match = leftVal && rightVal && leftVal.id === rightVal.id;

    //         } else if (laterality === "bilateral") {
    //             sharedVal = getSelectedValue(values, selectedShared);
    //             if (!sharedVal) return null;

    //             shared = formatValue(sharedVal);
    //             left = shared;
    //             right = shared;
                
    //             isPreferredShared = !!(sharedVal?.isPreferred ?? sharedVal?.isPreferredLeft ?? sharedVal?.isPreferredRight ?? false);
                
    //             match = true;
    //             const sharedExtra = (sharedVal?.price_extra || 0) * quantityToMake;
    //             leftTotal += sharedExtra;
    //             rightTotal += sharedExtra;
    //             priceExtra = sharedExtra * 2;
    //         } else {
    //             sharedVal = getSelectedValue(values, selectedShared);
    //             if (!sharedVal) return null;
    //             shared = formatValue(sharedVal);

    //             if (laterality === "left") {
    //                 left = shared;
    //                 isPreferredLeft = !!(sharedVal?.isPreferred ?? sharedVal?.isPreferredLeft ?? false);
    //                 const e = (sharedVal?.price_extra || 0) * quantityToMake;
    //                 leftTotal += e;
    //                 priceExtra = e;
    //             } else {
    //                 right = shared;
    //                 isPreferredRight = !!(sharedVal?.isPreferred ?? sharedVal?.isPreferredRight ?? false);
    //                 const e = (sharedVal?.price_extra || 0) * quantityToMake;
    //                 rightTotal += e;
    //                 priceExtra = e;
    //             }
    //         }

    //         return {
    //             key: `summary-${attr.id}`,
    //             label: attr.name,
    //             left,
    //             right,
    //             shared,
    //             isSplit: isSplitForAttr,
    //             match,
    //             priceExtra,
    //             note: !isSplitForAttr ? (sharedVal?.note || "") : undefined,
    //             noteLeft: isSplitForAttr ? (leftVal?.note || "") : undefined,
    //             noteRight: isSplitForAttr ? (rightVal?.note || "") : undefined,
    //             isPreferred: isSplitForAttr ? undefined : isPreferredShared,
    //             isPreferredLeft: isSplitForAttr ? isPreferredLeft : undefined,
    //             isPreferredRight: isSplitForAttr ? isPreferredRight : undefined,
    //         };
    //     }).filter((row) => row !== null);

    //     console.log("=== Summary Rows Built ===");
    //     console.log(result);

    //     const basePrice = productTemplate?.list_price || 0;
    //     const baseMultiplier = laterality === "bilateral" ? 2 : 1;
    //     const totalBase = basePrice * baseMultiplier * quantityToMake;
    //     const totalExtras = leftTotal + rightTotal;
    //     const total = totalBase + totalExtras;

    //     this.state.summary = [...result];
    //     if (typeof this.props.matrixPriceTotal === "number") {
    //         this.state.priceSummary = {
    //             base: 0,
    //             left: 0,
    //             right: 0,
    //             total: this.props.matrixPriceTotal,
    //             extrasSubtotal: 0,
    //         };
    //     } else {
    //         this.state.priceSummary = {
    //             base: totalBase,
    //             left: leftTotal,
    //             right: rightTotal,
    //             total,
    //             extrasSubtotal: totalExtras,
    //         };
    //     }
    //     if (this.summaryApi?.updateTotals) {
    //         this.summaryApi.updateTotals(this.state.priceSummary);
    //     }
    // }

    computeSummary(configOverride = {}) { 
        
        const {
            ptalIds = this.props.ptalIds || [],
            selected = this.props.selected || {},
            laterality = this.props.laterality || "bilateral",
            split = this.props.split || false,
            splitByAttrMap = this.props.splitByAttrMap || {},
            productTemplate = this.props.productTemplate,
            quantityToMake = this.props.quantityToMake || 1,
        } = configOverride || {};

        console.log("[SUMMARY] Config override received:", configOverride);

        const { left, right, shared } = getEffectiveSelectedBuckets(selected, split, laterality);
        const selectedLeft = flattenSelectedBucket(left);
        const selectedRight = flattenSelectedBucket(right);
        const selectedShared = flattenSelectedBucket(shared);

        let leftTotal = 0, rightTotal = 0;

        const flattenAttributes = (tree) => {
            const flat = [];
            const recurse = (nodes) => {
                for (const node of nodes) {
                    if (node.is_group && node.children) {
                        recurse(node.children);
                    } else {
                        flat.push(node);
                    }
                }
            };
            recurse(tree);
            return flat;
        };
        const allAttributes = flattenAttributes(ptalIds);

        const getSelectedValue = (values, dict) => {
            for (const v of values) {
                const key1 = v.x_virtual_cpq_id !== undefined ? String(v.x_virtual_cpq_id) : null;
                const key2 = String(v.id);
                if (key1 && dict.hasOwnProperty(key1)) {
                    const val = dict[key1];
                    return { ...v, ...(typeof val === "object" ? val : { value: val }) };
                }
                if (dict.hasOwnProperty(key2)) {
                    const val = dict[key2];
                    return { ...v, ...(typeof val === "object" ? val : { value: val }) };
                }
            }
            return null;
        };

        const formatValue = (val) => {
            if (!val) return "-";
            return val.is_custom && val.value ? `✍️ ${val.value}` : val.name || "-";
        };

        // console.log("[SUMMARY] Config override received:", configOverride);
        console.log("[SUMMARY] ptalIds", allAttributes.map(a => [a.id, a.name]));
        console.log("[SUMMARY] splitByAttrMap", splitByAttrMap);
        console.log("[SUMMARY] laterality:", laterality);
        console.log("[SUMMARY] selected.left", selectedLeft);
        console.log("[SUMMARY] selected.right", selectedRight);
        console.log("[SUMMARY] selected.shared", selectedShared);

        const result = allAttributes.map((attr) => {
        const values = attr.values || [];
        if (!attr.name || !values.length) return null;

        // Use per-attribute split for bilateral, else always shared
        const isSplitForAttr = laterality === "bilateral" && (splitByAttrMap[String(attr.id)] || split);

        let leftVal = null, rightVal = null, sharedVal = null;
        let left = "-", right = "-", shared = "-";
        let match = false, priceExtra = 0;
        let isPreferredLeft = false, isPreferredRight = false, isPreferredShared = false;

        if (isSplitForAttr) {
            // Try left/right buckets first, fallback to shared *only* if side is blank
            leftVal = getSelectedValue(values, selectedLeft);
            if (!leftVal && Object.keys(selectedShared).length)
                leftVal = getSelectedValue(values, selectedShared);

            rightVal = getSelectedValue(values, selectedRight);
            if (!rightVal && Object.keys(selectedShared).length)
                rightVal = getSelectedValue(values, selectedShared);

            // *** Fixed: Show summary row if either side has value ***
            // if (!leftVal && !rightVal) return null;

            if (!leftVal && !rightVal) {
                return {
                    key: `summary-${attr.id}`,
                    label: attr.name,
                    left: "⚠️",
                    right: "⚠️",
                    shared: "-",
                    isSplit: isSplitForAttr,
                    match: false,
                    priceExtra: 0,
                    noteLeft: "No selection",
                    noteRight: "No selection",
                };
            }


            left = formatValue(leftVal);
            right = formatValue(rightVal);

            isPreferredLeft = !!(leftVal?.isPreferredLeft ?? leftVal?.isPreferred ?? false);
            isPreferredRight = !!(rightVal?.isPreferredRight ?? rightVal?.isPreferred ?? false);

            const leftExtra = (leftVal?.price_extra || 0) * quantityToMake;
            const rightExtra = (rightVal?.price_extra || 0) * quantityToMake;
            leftTotal += leftExtra;
            rightTotal += rightExtra;
            priceExtra = leftExtra + rightExtra;
            match = leftVal && rightVal && leftVal.id === rightVal.id;

        } else if (laterality === "bilateral") {
            sharedVal = getSelectedValue(values, selectedShared);
            // if (!sharedVal) return null;

            if (!sharedVal) {
                return {
                    key: `summary-${attr.id}`,
                    label: attr.name,
                    shared: "⚠️",
                    left: "⚠️",
                    right: "⚠️",
                    isSplit: false,
                    match: false,
                    priceExtra: 0,
                    note: "No selection",
                };
            }
            shared = formatValue(sharedVal);
            left = shared;
            right = shared;
            isPreferredShared = !!(sharedVal?.isPreferred ?? sharedVal?.isPreferredLeft ?? sharedVal?.isPreferredRight ?? false);
            match = true;
            const sharedExtra = (sharedVal?.price_extra || 0) * quantityToMake;
            leftTotal += sharedExtra;
            rightTotal += sharedExtra;
            priceExtra = sharedExtra * 2;
        } else {
            if (laterality === "left") {
                leftVal = getSelectedValue(values, selectedLeft);
                if (!leftVal) return null;
                left = formatValue(leftVal);
                isPreferredLeft = !!(leftVal?.isPreferred ?? leftVal?.isPreferredLeft ?? false);
                const e = (leftVal?.price_extra || 0) * quantityToMake;
                leftTotal += e;
                priceExtra = e;
            } else if (laterality === "right") {
                rightVal = getSelectedValue(values, selectedRight);
                if (!rightVal) return null;
                right = formatValue(rightVal);
                isPreferredRight = !!(rightVal?.isPreferred ?? rightVal?.isPreferredRight ?? false);
                const e = (rightVal?.price_extra || 0) * quantityToMake;
                rightTotal += e;
                priceExtra = e;
            } else {
                sharedVal = getSelectedValue(values, selectedShared);
                if (!sharedVal) return null;
                shared = formatValue(sharedVal);
                left = shared;
                right = shared;
                isPreferredShared = !!(sharedVal?.isPreferred ?? sharedVal?.isPreferredLeft ?? sharedVal?.isPreferredRight ?? false);
                const sharedExtra = (sharedVal?.price_extra || 0) * quantityToMake;
                leftTotal += sharedExtra;
                rightTotal += sharedExtra;
                priceExtra = sharedExtra * 2;
            }
        }

        return {
            key: `summary-${attr.id}`,
            label: attr.name,
            left,
            right,
            shared,
            isSplit: isSplitForAttr,
            match,
            priceExtra,
            note: !isSplitForAttr ? (sharedVal?.note || "") : undefined,
            noteLeft: isSplitForAttr ? (leftVal?.note || "") : undefined,
            noteRight: isSplitForAttr ? (rightVal?.note || "") : undefined,
            isPreferred: isSplitForAttr ? undefined : isPreferredShared,
            isPreferredLeft: isSplitForAttr ? isPreferredLeft : undefined,
            isPreferredRight: isSplitForAttr ? isPreferredRight : undefined,
        };
    }).filter((row) => row !== null);

        console.log("=== Summary Rows Built ===", result);

        const basePrice = productTemplate?.list_price || 0;
        const baseMultiplier = laterality === "bilateral" ? 2 : 1;
        const totalBase = basePrice * baseMultiplier * quantityToMake;
        const totalExtras = leftTotal + rightTotal;
        const total = totalBase + totalExtras;

        this.state.summary = [...result];
        if (typeof this.props.matrixPriceTotal === "number") {
            this.state.priceSummary = {
                base: 0, left: 0, right: 0,
                total: this.props.matrixPriceTotal,
                extrasSubtotal: 0,
            };
        } else {
            this.state.priceSummary = {
                base: totalBase,
                left: leftTotal,
                right: rightTotal,
                total,
                extrasSubtotal: totalExtras,
            };
        }
        if (this.summaryApi?.updateTotals) {
            this.summaryApi.updateTotals(this.state.priceSummary);
        }
    }

    // --------- Group renderers with shared logic -------------
    renderGroup(group) {
        const selected = this.props.selected || {};
        const isSplit = this.props.split;
        const laterality = this.props.laterality;
        const { left: selectedLeft, right: selectedRight, shared: selectedShared } =
            getEffectiveSelectedBuckets(selected.shared, isSplit, laterality);
        const renderChild = (attr) => {
            if (attr.is_group) {
                return this.renderGroup(attr);
            }
            const values = attr.values || [];
            const findSelectedVal = (dict) => values.find(val => dict?.[val.id]);

            const selLeft = findSelectedVal(selectedLeft);
            const selRight = findSelectedVal(selectedRight);
            const selShared = findSelectedVal(selectedShared);

            const shouldShow = isSplit ? (selLeft || selRight) : selShared;
            if (!shouldShow) return null;

            const left = selLeft?.name || "-";
            const right = selRight?.name || "-";
            const shared = selShared?.name || "-";

            return html`
                <div class="ps-3">
                    <strong>${attr.name}</strong>:
                    ${isSplit
                        ? html`<span>L: ${left}, R: ${right}</span>`
                        : html`${shared}`}
                </div>
            `;
        };

        const children = (group.children || []).map(renderChild).filter(Boolean);

        if (!children.length) return null;

        return html`
            <div class="mb-3 border-start ps-3">
                <h5 class="mb-1">${group.name}</h5>
                ${children}
            </div>
        `;
    }
    
    renderGroupHtmlString(group) {
        const selected = this.props.selected || {};
        const isSplit = this.props.split;
        const laterality = this.props.laterality;
        const { left: selectedLeft, right: selectedRight, shared: selectedShared } =
            getEffectiveSelectedBuckets(selected, isSplit, laterality);

        const renderChild = (attr) => {
            if (attr.is_group) {
                return this.renderGroupHtmlString(attr);
            }
            const values = attr.values || [];
            const findSelectedVal = (dict) => values.find(val => dict?.[val.id]);
            const selLeft = findSelectedVal(selectedLeft);
            const selRight = findSelectedVal(selectedRight);
            const selShared = findSelectedVal(selectedShared);

            const shouldShow = isSplit ? (selLeft || selRight) : selShared;
            if (!shouldShow) return "";

            const left = selLeft?.name || "-";
            const right = selRight?.name || "-";
            const shared = selShared?.name || "-";

            return `<div class="ps-3">
                <strong>${attr.name}</strong>: ${isSplit ? `L: ${left}, R: ${right}` : shared}
            </div>`;
        };

        const childrenHtml = (group.children || [])
            .map(renderChild)
            .filter(Boolean)
            .join("");

        if (!childrenHtml) return "";

        return `<div class="mb-3 border-start ps-3">
            <h5 class="mb-1">${group.name}</h5>
            ${childrenHtml}
        </div>`;
    }

    summaryJson() {
        try {
            return JSON.stringify(this.state.summary, null, 2);
        } catch (e) {
            return '[summary stringify failed]';
        }
    }

    async printSummary() {
        let qrDataUrl = null;
        if (this.realLineId?.value) {
            qrDataUrl = await this.generateQrDataUrl(this.rpc, this.realLineId.value);
        }

        const summaryTable = this.state.summary.map(row => ({
            Attribute: row.label,
            Left: row.left || "-",
            Right: row.right || "-",
            Shared: row.shared || "-",
            Match: row.isSplit ? (row.match ? "✔️" : "❌") : "✔️",
            Price: `$${(row.priceExtra || 0).toFixed(2)}`,
            Note: row.note || row.noteLeft || row.noteRight || "",
        }));

        console.log("About to print summary table");
        console.debug("[ConfiguratorSummaryPanel] Summary table:");
        console.table(summaryTable);

        const summaryHtml = this._generatePrintHtml(qrDataUrl);
        const printWindow = window.open("", "Print Summary", "width=800,height=600");
        if (printWindow) {
            printWindow.document.open();
            printWindow.document.write(summaryHtml);
            printWindow.document.close();
            printWindow.focus();
            printWindow.print();
        } else {
            this.notification?.add("Popup blocked. Please allow popups to print.", { type: "warning" });
        }
    }

    _generatePrintHtml(qrDataUrl = null) {
        const pb = this.state.priceSummary || {};
        const summaryRows = this.state.summary || [];

        const clean = (val) => {
            if (typeof val === "string") return val.trim() || "-";
            if (val != null) return String(val).trim() || "-";
            return "-";
        };

        const rows = summaryRows.map(s => {
            const isSplit = s.isSplit;
            const left = clean(s.left);
            const right = clean(s.right);
            const shared = clean(s.shared);
            const match = isSplit ? (s.match ? "✔️" : "❌") : "✔️";

            return isSplit ? `
                <tr>
                    <td>${s.label}</td>
                    <td>${left}</td>
                    <td>${right}</td>
                    <td>${match}</td>
                    <td>$${(s.priceExtra || 0).toFixed(2)}</td>
                    <td>
                        ${s.noteLeft ? `<div><small class="text-muted">LT: ${s.noteLeft}</small></div>` : ""}
                        ${s.noteRight ? `<div><small class="text-muted">RT: ${s.noteRight}</small></div>` : ""}
                    </td>
                </tr>
            ` : `
                <tr>
                    <td>${s.label}</td>
                    <td colspan="2">${shared}</td>
                    <td>${s.match ? "✔️" : "—"}</td>
                    <td>$${(s.priceExtra || 0).toFixed(2)}</td>
                    <td>
                        ${s.note ? `<small class="text-muted">${s.note}</small>` : ""}
                    </td>
                </tr>
            `;
        }).join("");

        const hasVisibleRows = rows.trim().length > 0;

        const fallbackMessage = `
            <tr>
                <td colspan="6" style="text-align: center; font-style: italic; color: #888;">
                    🟡 No configuration options selected yet.
                </td>
            </tr>
        `;

        const matrixBadge = this.props.matrixOverrideActive
            ? `<p><span class="badge bg-warning text-dark">Price overridden by matrix</span></p>`
            : "";

        let groupSection = "";
        if (this.props.ptalIds?.some(g => g.is_group)) {
            const topLevelGroups = this.props.ptalIds.filter(g => g.is_group);
            groupSection = `<hr/><h3>Structured Group View</h3>` +
                topLevelGroups.map(g => this._generateGroupHtml(g)).filter(Boolean).join("");
        }

        return `
            <html>
            <head>
                <title>Configuration Summary</title>
                <style>
                    body { font-family: sans-serif; margin: 20px; }
                    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                    th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
                    th { background: #f0f0f0; }
                    .totals { font-weight: bold; }
                    .badge { display: inline-block; padding: 5px 10px; background: #ffc107; color: #000; border-radius: 4px; font-size: 0.9em; }
                </style>
            </head>
            <body>
                <h2>Product Configuration Summary</h2>
                <p><b>Product:</b> ${this.productTemplate?.display_name || "-"}</p>
                <p><b>Quantity:</b> ${this.props.quantityToMake}</p>
                <table>
                    <thead>
                        <tr>
                            <th>Attribute</th>
                            <th>Left / Shared</th>
                            <th>Right</th>
                            <th>Match</th>
                            <th>Price</th>
                            <th>Note</th>
                        </tr>
                    </thead>
                    <tbody>${hasVisibleRows ? rows : fallbackMessage}</tbody>
                </table>
                <div class="totals">
                    <p>💸 Base Price: $${pb.base?.toFixed(2) || "0.00"}</p>
                    <p>➕ Extras: $${pb.extrasSubtotal?.toFixed(2) || "0.00"}</p>
                    <p>Subtotal: $${pb.subtotal?.toFixed(2) || "0.00"}</p>
                    <p>× Quantity: ${pb.quantity || this.props.quantityToMake}</p>
                    <p>📊 Final Total: <b>$${pb.total?.toFixed(2) || "0.00"}</b></p>
                    ${matrixBadge}
                    ${groupSection}
                </div>
                ${qrDataUrl ? `
                    <hr/>
                    <div style="text-align:center;margin-top:16px;">
                        <img src="${qrDataUrl}" width="128" height="128" alt="QR Code" />
                        <div style="font-size:0.85em;color:#666;">Scan for full configuration</div>
                    </div>
                ` : ""}
            </body>
            </html>
        `;
    }

    _generateGroupHtml(group) {
        const selected = this.props.selected || {};
        const isSplit = this.props.split;
        const laterality = this.props.laterality;
        const { left: selectedLeft, right: selectedRight, shared: selectedShared } =
            getEffectiveSelectedBuckets(selected, isSplit, laterality);

        const renderChild = (attr) => {
            if (attr.is_group) {
                const rendered = this._generateGroupHtml(attr);
                return rendered ? rendered : "";
            }

            const values = attr.values || [];
            const findSelectedVal = (dict) => values.find(v => dict?.[v.id]);

            const selLeft = findSelectedVal(selectedLeft);
            const selRight = findSelectedVal(selectedRight);
            const selShared = findSelectedVal(selectedShared);

            const shouldShow = isSplit ? (selLeft || selRight) : selShared;
            if (!shouldShow) return ""; // Skip if no selected value

            let left = "-", right = "-", shared = "-";
            if (laterality === "bilateral" && isSplit) {
                left = selLeft?.name || "-";
                right = selRight?.name || "-";
            } else {
                shared = selShared?.name || "-";
            }

            return `<div style="margin-left: 20px;">
                <strong>${attr.name}</strong>: ${isSplit ? `L: ${left}, R: ${right}` : shared}
            </div>`;
        };

        const childrenHtml = (group.children || [])
            .map(renderChild)
            .filter(Boolean)
            .join("");

        if (!childrenHtml) return ""; // Skip group if no visible children

        return `<div style="margin-top: 12px;">
            <h4 style="margin-bottom: 6px;">${group.name}</h4>
            ${childrenHtml}
        </div>`;
    }
    
    pulseElement(selector) {
        const element = document.querySelector(selector);
        if (!element) return;

        element.classList.remove("highlight-success");
        void element.offsetWidth;
        element.classList.add("highlight-success");
    }
}

ConfiguratorSummaryPanel.template = "cpq.ConfiguratorSummaryPanel";
ConfiguratorSummaryPanel.props = {
    ptalIds: Array,
    selected: Object,
    laterality: String,
    split: Boolean,
    splitByAttrMap: { type: Object, optional: true, default: () => ({}) },
    productTemplate: Object,
    quantityToMake: Number,
    register: Function,
    matrixPriceTotal: { type: Number, optional: true },
    matrixOverrideActive: { type: Boolean, optional: true },  
    record: { type: Object, optional: true },
    lineId: { type: [Number, String], optional: true },
};
