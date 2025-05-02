/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUpdateProps, onWillUnmount } from "@odoo/owl";
import { debounce } from "./utils.esm";

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

        const debouncedRecomputeSummary = debounce(() => {
            console.log("🧩 Debounced recompute summary");
            requestAnimationFrame(() => {
                this._preserveScroll(() => this.computeSummary());
            });
        }, 150);

        const debouncedAdjustHeight = debounce(() => {
            console.log("📏 Debounced adjustHeight");
            this.adjustHeight();
        }, 150);

        onMounted(() => {
            console.log("📌 SummaryPanel mounted");

            if (props.ptalIds?.length > 0) {
                console.log("🧩 Initial ptalIds detected, computing summary...");
                this.computeSummary();
            }

            this.adjustHeight();
        });

        onWillUpdateProps((nextProps) => {
            let needsRecompute = false;
            let needsHeightAdjust = false;

            if (nextProps.quantityToMake !== this.state.quantityToMake) {
                console.log("🔄 Quantity changed:", nextProps.quantityToMake);
                this.state.quantityToMake = nextProps.quantityToMake;
                needsRecompute = true;
                needsHeightAdjust = true;
            }

            if (nextProps.laterality !== props.laterality) {
                console.log("🔄 Laterality changed:", nextProps.laterality);
                props.laterality = nextProps.laterality;
                needsRecompute = true;
                needsHeightAdjust = true;
            }

            if (nextProps.split !== props.split) {
                console.log("🔄 Split mode changed:", nextProps.split);
                props.split = nextProps.split;
                needsRecompute = true;
                needsHeightAdjust = true;
            }

            if (nextProps.selected !== props.selected) {
                console.log("🔄 Selected attributes changed.");
                props.selected = nextProps.selected;
                needsRecompute = true;
            }

            if (nextProps.ptalIds !== props.ptalIds) {
                console.log("🔄 PTAL IDs changed (attribute structure).");
                props.ptalIds = nextProps.ptalIds;
                needsRecompute = true;
                needsHeightAdjust = true;
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

        // After computing totalBase, totalExtras, total...

        // 🔁 Use matrix price if provided via props
        if (typeof this.props.matrixPriceTotal === "number") {
            const matrixTotal = this.props.matrixPriceTotal;
        
            this.state.priceSummary = {
                base: 0,
                left: 0,
                right: 0,
                total: matrixTotal,
                extrasSubtotal: 0,
            };
        
            console.log("📦 Matrix price override applied:", matrixTotal);
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

        const matrixBadge = this.props.matrixOverrideActive
        ? `<p><span class="badge bg-warning text-dark">⚡ Price overridden by matrix</span></p>`
        : "";

        // ${this.props.matrixOverrideActive ? `<p><strong>⚡ Price overridden by matrix</strong></p>` : ""}


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
                    ${matrixBadge}
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
    matrixPriceTotal: { type: Number, optional: true },
    matrixOverrideActive: { type: Boolean, optional: true },  
};
