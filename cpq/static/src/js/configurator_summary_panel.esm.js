/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUpdateProps, onWillUnmount } from "@odoo/owl";
import { debounce, generateQrCodeUnified } from "./utils.esm";

function formatCurrency(amount) {
    const number = typeof amount === "number" ? amount : parseFloat(amount) || 0;
    return `$${number.toFixed(2)}`;
}

export default class ConfiguratorSummaryPanel extends Component {

    setup() {
        super.setup();
    
        const props = this.props;
        this.productTemplate = props.productTemplate;
        this.formatCurrency = formatCurrency;
        this.summaryWrapper = useRef("summaryWrapper");
        this.toastQueue = [];
    
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
    
        this._registerExternalApi();
        this._setupDebouncers();
        this.debouncedQrGeneration = debounce(() => {
            this._handleQrGeneration();
        }, 200);
        
    
        // onMounted(this._onMountedHandler.bind(this));
        onWillUpdateProps(this._onPropsUpdateHandler.bind(this));
        onWillUnmount(this._onWillUnmountHandler.bind(this));
    
        this.computeSummary();
        console.log("🧠 Initial computeSummary:", this.state.quantityToMake);
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
            });
        }
    }
    
    _setupDebouncers() {
        this.debouncedRecomputeSummary = debounce(() => {
            console.log("🧩 Debounced recompute summary");
            requestAnimationFrame(() => {
                this._preserveScroll(() => this.computeSummary());
            });
        }, 150);
    
        this.debouncedAdjustHeight = debounce(() => {
            console.log("📏 Debounced adjustHeight");
            this.adjustHeight();
        }, 150);
    }
    
    _onPropsUpdateHandler(nextProps) {
        const { quantityToMake, laterality, split, selected, ptalIds } = nextProps;
        let needsRecompute = false;
        let needsHeightAdjust = false;
    
        if (quantityToMake !== this.state.quantityToMake) {
            this.state.quantityToMake = quantityToMake;
            needsRecompute = true;
            needsHeightAdjust = true;
        }
        if (laterality !== this.props.laterality) {
            this.props.laterality = laterality;
            needsRecompute = true;
            needsHeightAdjust = true;
        }
        if (split !== this.props.split) {
            this.props.split = split;
            needsRecompute = true;
            needsHeightAdjust = true;
        }
        if (selected !== this.props.selected) {
            this.props.selected = selected;
            needsRecompute = true;
        }
        if (ptalIds !== this.props.ptalIds) {
            this.props.ptalIds = ptalIds;
            needsRecompute = true;
            needsHeightAdjust = true;
        }
    
        if (needsRecompute) this.debouncedRecomputeSummary();
        if (needsHeightAdjust) this.debouncedAdjustHeight();
    
        // ✅ Add the QR refresh call here:
        // this.debouncedQrGeneration();
        this._handleQrGeneration(nextProps);
        
    }
    
    _onWillUnmountHandler() {
        if (this.debouncedQrGeneration) {
            this.debouncedQrGeneration = null;
        }
        
        clearTimeout(this._heightTimeout);
        clearTimeout(this._toastTimeout);
        this.toastQueue = [];
    }

    async _handleQrGeneration(props = this.props) {
        if (!this.el) {
            console.warn("🚫 Skipping QR generation — component element not available.");
            return;
        }
    
        const orderId = props.orderId;
        const lineId = props.record?.resId || null;
        const templateId = props.productTemplate?.id || null;
        const configHash = props.record?.data?.cpq_configuration_hash || null;
    
        const validOrderId = typeof orderId === "number";
        const validLineId = typeof lineId === "number" && lineId > 0;
        const validTemplateId = typeof templateId === "number";
    
        // Dynamically find the correct canvas (order-level or line-level)
        const canvas =
            this.el.querySelector('.cpq-order-line-qr-canvas') ||
            this.el.querySelector('.cpq-order-qr-canvas');
    
        if (!canvas) {
            console.warn("⚠️ Skipping QR generation — no QR canvas found.");
            return;
        }
    
        // Determine generation mode based on the presence of lineId
        const qrPayloadData = {
            orderId,
            templateId,
            configHash,
            ...(validLineId ? { lineId } : {}), // Only include lineId if valid
        };
    
        if (validOrderId && validTemplateId) {
            console.log("🟢 Generating QR code with payload:", qrPayloadData);
            generateQrCodeUnified(qrPayloadData, canvas, true); // true = debug
        } else {
            console.warn("⚠️ Skipping QR generation — invalid identifiers:", {
                orderId,
                lineId,
                templateId,
                configHash,
                hasCanvas: !!canvas,
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

            const targetHeight = table.offsetHeight + 16; // + padding
            if (this.state.height !== targetHeight) {
                console.log(`📏 Adjusting summary height: ${targetHeight}px`);
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
    
    // Handles shared and split + proper bilateral pricing logic
    computeSummary() {
        console.log("🧠 Computing summary...");
        const {
            ptalIds = [],
            selected = {},
            laterality,
            split,
            productTemplate,
            quantityToMake = 1,
        } = this.props;
    
        const selectedLeft = selected.left || {};
        const selectedRight = selected.right || {};
        const isSplit = laterality === "bilateral" && split;
    
        let leftTotal = 0;
        let rightTotal = 0;
    
        const result = ptalIds.map((attr, index) => {
            if (!attr || !attr.name || !Array.isArray(attr.ptav_ids)) {
                return {
                    key: `summary-invalid-${index}`,
                    label: "⚠️ Invalid Attribute",
                    left: "-",
                    right: "-",
                    shared: "-",
                    priceExtra: 0,
                };
            }
    
            const ptavs = attr.ptav_ids;
            const getSelectedPtav = (ptavs, selectedDict) =>
                ptavs.find((ptav) => ptav.id in selectedDict) || null;
    
            let left = "-", right = "-", shared = "-", priceExtra = 0;
    
            if (isSplit) {
                const leftPtav = getSelectedPtav(ptavs, selectedLeft);
                const rightPtav = getSelectedPtav(ptavs, selectedRight);
    
                left = leftPtav?.name || "-";
                right = rightPtav?.name || "-";
    
                const leftExtra = (leftPtav?.price_extra || 0) * quantityToMake;
                const rightExtra = (rightPtav?.price_extra || 0) * quantityToMake;
    
                leftTotal += leftExtra;
                rightTotal += rightExtra;
                priceExtra = leftExtra + rightExtra;
    
            } else {
                const sharedPtav = getSelectedPtav(ptavs, selected);
                shared = sharedPtav?.name || "-";
                const sharedExtra = (sharedPtav?.price_extra || 0) * quantityToMake;
    
                if (laterality === "left") {
                    left = shared;
                    leftTotal += sharedExtra;
                    priceExtra = sharedExtra;
                } else if (laterality === "right") {
                    right = shared;
                    rightTotal += sharedExtra;
                    priceExtra = sharedExtra;
                } else if (laterality === "bilateral") {
                    left = shared;
                    right = shared;
                    const bilateralExtra = sharedExtra * 2;
                    leftTotal += bilateralExtra / 2;
                    rightTotal += bilateralExtra / 2;
                    priceExtra = bilateralExtra;
                }
            }
    
            return {
                key: `summary-${attr.id}`,
                label: attr.name,
                left,
                right,
                shared,
                priceExtra,
            };
        });
    

        const basePrice = productTemplate?.list_price || 0;
        // const basePrice = this.props.productTemplate?.list_price || 0;
        const baseMultiplier = laterality === "bilateral" ? 2 : 1;
        const totalBase = basePrice * baseMultiplier * quantityToMake;
        const totalExtras = leftTotal + rightTotal;
        const total = totalBase + totalExtras;
    
        this.state.summary = result;
        this.state.priceSummary = {
            base: totalBase,
            left: leftTotal,
            right: rightTotal,
            total,
            extrasSubtotal: totalExtras,
        };
    
        if (this.summaryApi?.updateTotals) {
            this.summaryApi.updateTotals(this.state.priceSummary);
        }
    
        console.log("✅ Final summary computed:", result);
    }
    

    printSummary() {
        const summaryHtml = this._generatePrintHtml();
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
    
    _generatePrintHtml() {
        const pb = this.state.priceSummary || {};
        const rows = this.state.summary.map(s => {
            return `<tr>
                <td>${s.label}</td>
                <td>${s.shared ?? s.left ?? "-"}</td>
                ${this.props.split ? `<td>${s.right ?? "-"}</td><td>${s.left === s.right ? "✅" : "❌"}</td>` : ""}
                <td>$${(s.priceExtra || 0).toFixed(2)}</td>
            </tr>`;
        }).join("");
    
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
                </style>
            </head>
            <body>
                <h2>📝 Product Configuration Summary</h2>
                <p><b>Product:</b> ${this.productTemplate?.display_name || "-"}</p>
                <p><b>Quantity:</b> ${this.props.quantityToMake}</p>
    
                <table>
                    <thead>
                        <tr>
                            <th>Attribute</th>
                            <th>${this.props.split ? "Left" : "Value"}</th>
                            ${this.props.split ? "<th>Right</th><th>Match</th>" : ""}
                            <th>Price</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
    
                <div class="totals">
                    <p>💸 Base Price: $${pb.base?.toFixed(2) || "0.00"}</p>
                    <p>➕ Extras: $${pb.extrasSubtotal?.toFixed(2) || "0.00"}</p>
                    <p>📦 Subtotal: $${pb.subtotal?.toFixed(2) || "0.00"}</p>
                    <p>× Quantity: ${pb.quantity || this.props.quantityToMake}</p>
                    <p>📊 Final Total: <b>$${pb.total?.toFixed(2) || "0.00"}</b></p>
                </div>
            </body>
            </html>
        `;
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
    productTemplate: Object,
    quantityToMake: Number,
    register: Function,
};
