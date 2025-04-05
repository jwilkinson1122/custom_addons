/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUpdateProps } from "@odoo/owl";

function formatCurrency(amount) {
    const number = typeof amount === "number" ? amount : parseFloat(amount) || 0;
    return `$${number.toFixed(2)}`;
}

export default class ConfiguratorSummaryPanel extends Component {
    
    setup() {
        super.setup();
        this.formatCurrency = formatCurrency;
        this.summaryWrapper = useRef("summaryWrapper");

        this.state = useState({
            summary: [],
            priceSummary: {
                base: 0,
                left: 0,
                right: 0,
                shared: 0,
                total: 0,
                extrasSubtotal: 0,
            },
            expanded: true,
            height: 0,
            showExtras: false, // ⬅️ For toggling
            quantityToMake: this.props.quantityToMake || 1,
        });

        this.toggleExtras = () => {
            this.state.showExtras = !this.state.showExtras;
        };
        
        onMounted(() => {
            console.log("📌 SummaryPanel mounted");
            this.adjustHeight();
        });
        
        onWillUpdateProps((nextProps) => {
            if (nextProps.quantityToMake !== this.state.quantityToMake) {
                console.log("🔄 Syncing quantityToMake from props to state:", nextProps.quantityToMake);
                this.state.quantityToMake = nextProps.quantityToMake;
        
                // 💡 Delay computeSummary until after reactivity completes
                requestAnimationFrame(() => {
                    this._preserveScroll(() => this.computeSummary());
                });
            } else {
                // 🌀 Other props changed → still recompute summary
                this._preserveScroll(() => this.computeSummary());
            }
            
        });
        
        
        this.computeSummary();
        console.log("🧠 computeSummary triggered after quantity sync:", this.state.quantityToMake);

    }

    toggleExpand() {
        this.state.expanded = !this.state.expanded;
        this.adjustHeight();
    }

    // 💡 Smooth scroll-preserving wrapper
    _preserveScroll(fn) {
        const scrollY = this.summaryWrapper?.el?.scrollTop || 0;
        fn();
        setTimeout(() => {
            if (this.summaryWrapper?.el) {
                this.summaryWrapper.el.scrollTop = scrollY;
            }
        }, 0);
    }

    adjustHeight() {
        clearTimeout(this._heightTimeout);
        this._heightTimeout = setTimeout(() => {
            const el = this.summaryWrapper.el;
            if (!el) return;
    
            if (this.state.expanded) {
                el.style.height = "auto";
                const fullHeight = el.scrollHeight;
                el.style.height = "0px";
                void el.offsetHeight;
                this.state.height = fullHeight || el.offsetHeight;
            } else {
                this.state.height = 0;
            }
        }, 20); // debounce: wait 1 frame to stabilize layout
    }

    computeSummary() {
        console.log("🧠 Computing summary...");
    
        const {
            ptalIds = [],
            selected = {},
            laterality,
            split,
        } = this.props;
    
        const selectedLeft = selected.left || {};
        const selectedRight = selected.right || {};
        const isSplit = laterality === "bilateral" && split;
        
        const quantityToMake = this.state.quantityToMake || 1;
        console.log("🧾 quantityToMake (from state) in computeSummary:", quantityToMake);
        // const quantityToMake = this.props.quantityToMake || 1;

        let leftTotal = 0;
        let rightTotal = 0;
        let totalExtras = 0;
    
        const getSelectedPtav = (ptavs, selectedDict) => {
            for (const ptav of ptavs) {
                if (Object.prototype.hasOwnProperty.call(selectedDict, ptav.id)) {
                    return ptav;
                }
            }
            return null;
        };
    
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
            let left = "-", right = "-", shared = "-";
            let priceExtra = 0;
    
            if (isSplit) {
                const leftPtav = getSelectedPtav(ptavs, selectedLeft);
                const rightPtav = getSelectedPtav(ptavs, selectedRight);
    
                left = leftPtav?.name || "-";
                right = rightPtav?.name || "-";
    
                // const leftExtra = leftPtav?.price_extra || 0;
                // const rightExtra = rightPtav?.price_extra || 0;

                const leftExtra = (leftPtav?.price_extra || 0) * quantityToMake;
                const rightExtra = (rightPtav?.price_extra || 0) * quantityToMake;
    
                leftTotal += leftExtra;
                rightTotal += rightExtra;
                priceExtra = leftExtra + rightExtra;
            } else {
                const sharedPtav = getSelectedPtav(ptavs, selected);
                shared = sharedPtav?.name || "-";
                const sharedExtra = sharedPtav?.price_extra || 0;

                if (laterality === "left") {
                    left = shared;
                    const extra = sharedExtra * quantityToMake;
                    leftTotal += extra;
                    priceExtra = extra;
                } else if (laterality === "right") {
                    right = shared;
                    const extra = sharedExtra * quantityToMake;
                    rightTotal += extra;
                    priceExtra = extra;
                } else if (laterality === "bilateral") {
                    left = shared;
                    right = shared;
                    const extra = sharedExtra * 2 * quantityToMake;
                    leftTotal += extra / 2;
                    rightTotal += extra / 2;
                    priceExtra = extra;
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
    
        const basePrice = this.props.productTmplId?.list_price || 0;
        const isBilateral = laterality === "bilateral";
        const totalBase = (isBilateral ? basePrice * 2 : basePrice) * quantityToMake;

        totalExtras = leftTotal + rightTotal;
        const total = totalBase + totalExtras;

        this.state.summary = result;
        this.state.priceSummary = {
            base: totalBase,
            left: leftTotal,
            right: rightTotal,
            total,
            extrasSubtotal: totalExtras,
        };
    
        console.log("✅ Final summary:", result);
        console.log("📦 Extras Subtotal:", totalExtras);
        console.log("💰 Total:", total);
    }
    
    printSummary() {
        const printContents = this.summaryWrapper.el?.outerHTML;
        if (!printContents) return;
    
        const win = window.open("", "_blank");
        if (!win) {
            console.warn("🚫 Failed to open print window.");
            return;
        }
    
        const doc = win.document;
    
        doc.open();  // 🔄 Explicitly open the document (avoids the deprecation warning)
        doc.write(`
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Configuration Summary</title>
                    <style>
                        body { font-family: sans-serif; padding: 20px; }
                        h1 { text-align: center; }
                        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
                        .price-summary { margin-top: 20px; font-size: 1.1em; }
                    </style>
                </head>
                <body>
                    <h1>${this.props.productTmplId.display_name}</h1>
                    ${printContents}
                </body>
            </html>
        `);
        doc.close();  // ✅ Always close the document to finalize it
        win.focus();
        win.print();
        win.close();
    }
    
 
}

ConfiguratorSummaryPanel.template = "cpq.ConfiguratorSummaryPanel";

ConfiguratorSummaryPanel.props = {
    ptalIds: Array,
    selected: Object,
    laterality: String,
    split: Boolean,
    productTmplId: Object,
    quantityToMake: Number,
    register: Function,
};


