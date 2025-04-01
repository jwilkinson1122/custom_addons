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

        // this.state = useState({
        //     summary: [],
        //     priceSummary: { left: 0, right: 0, total: 0 },
        //     expanded: true,
        //     height: 0,
        // });

        this.state = useState({
            summary: [],
            priceSummary: {
                base: 0,
                left: 0,
                right: 0,
                shared: 0,     // ✅ include shared
                total: 0,
            },
            expanded: true,
            height: 0,
        });
        
        onMounted(() => {
            console.log("📌 SummaryPanel mounted");
            this.adjustHeight();
        });
        
        onWillUpdateProps(() => {
            console.log("🌀 Props updated → recomputing summary...");
            this._preserveScroll(() => this.computeSummary());
        });
    

        this.computeSummary();
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

    

    // Current Method
    // computeSummary() {
    //     console.log("🧠 Computing summary...");
    
    //     const {
    //         ptalIds = [],
    //         selected = {},
    //         laterality,
    //         split,
    //         productTmplId,
    //         quantityToMake = 1,
    //     } = this.props;
    
    //     const selectedLeft = selected.left || {};
    //     const selectedRight = selected.right || {};
    //     const isSplit = laterality === "bilateral" && split;
    
    //     let leftTotal = 0;
    //     let rightTotal = 0;
    
    //     const getSelectedPtav = (ptavs, selectedDict) => {
    //         for (const ptav of ptavs) {
    //             if (Object.prototype.hasOwnProperty.call(selectedDict, ptav.id)) {
    //                 return ptav;
    //             }
    //         }
    //         return null;
    //     };
    
    //     const result = ptalIds.map((attr, index) => {
    //         if (!attr || !attr.name || !Array.isArray(attr.ptav_ids)) {
    //             return {
    //                 key: `summary-invalid-${index}`,
    //                 label: "⚠️ Invalid Attribute",
    //                 left: "-",
    //                 right: "-",
    //                 shared: "-",
    //                 priceExtra: 0,
    //             };
    //         }
    
    //         const ptavs = attr.ptav_ids;
    //         let left = "-", right = "-", shared = "-";
    //         let priceExtra = 0;
    
    //         if (isSplit) {
    //             const leftPtav = getSelectedPtav(ptavs, selectedLeft);
    //             const rightPtav = getSelectedPtav(ptavs, selectedRight);
    
    //             left = leftPtav?.name || "-";
    //             right = rightPtav?.name || "-";
    
    //             const leftExtra = leftPtav?.price_extra || 0;
    //             const rightExtra = rightPtav?.price_extra || 0;
    
    //             leftTotal += leftExtra;
    //             rightTotal += rightExtra;
    //             priceExtra = leftExtra + rightExtra;
    
    //         } else {
    //             const sharedPtav = getSelectedPtav(ptavs, selected);
    //             shared = sharedPtav?.name || "-";
    //             priceExtra = sharedPtav?.price_extra || 0;
    
    //             if (laterality === "left") {
    //                 left = shared;
    //                 leftTotal += priceExtra;
    //             } else if (laterality === "right") {
    //                 right = shared;
    //                 rightTotal += priceExtra;
    //             } else if (laterality === "bilateral") {
    //                 left = shared;
    //                 right = shared;
    //                 leftTotal += priceExtra;
    //                 rightTotal += priceExtra;
    //             }
    //         }
    
    //         return {
    //             key: `summary-${attr.id}`,
    //             label: attr.name,
    //             left,
    //             right,
    //             shared,
    //             priceExtra,
    //         };
    //     });
    
    //     const basePrice = productTmplId?.list_price || 0;
    //     const isBilateral = laterality === "bilateral";
    //     const totalBase = isBilateral ? basePrice * 2 : basePrice;
    
    //     const priceSummary = {
    //         base: totalBase,
    //         left: leftTotal,
    //         right: rightTotal,
    //         total: (totalBase + leftTotal + rightTotal) * quantityToMake,
    //     };
    
    //     this.state.summary = result;
    //     this.state.priceSummary = priceSummary;
    
    //     console.log("✅ Final summary:", result);
    //     console.log("💰 Price summary:", priceSummary);
    // }

    computeSummary() {
        console.log("🧠 Computing summary...");
    
        const {
            ptalIds = [],
            selected = {},
            laterality,
            split,
            productTmplId,
            quantityToMake = 1,
        } = this.props;
    
        const selectedLeft = selected.left || {};
        const selectedRight = selected.right || {};
        const isSplit = laterality === "bilateral" && split;
    
        let leftTotal = 0;
        let rightTotal = 0;
        let sharedTotal = 0;
    
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
    
                const leftExtra = leftPtav?.price_extra || 0;
                const rightExtra = rightPtav?.price_extra || 0;
    
                leftTotal += leftExtra;
                rightTotal += rightExtra;
                priceExtra = leftExtra + rightExtra;  // for display only
    
            } else {
                const sharedPtav = getSelectedPtav(ptavs, selected);
                shared = sharedPtav?.name || "-";
                priceExtra = sharedPtav?.price_extra || 0;
    
                sharedTotal += priceExtra;
    
                if (laterality === "left") {
                    left = shared;
                    leftTotal += priceExtra;
                } else if (laterality === "right") {
                    right = shared;
                    rightTotal += priceExtra;
                } else if (laterality === "bilateral") {
                    left = shared;
                    right = shared;
                    leftTotal += priceExtra;
                    rightTotal += priceExtra;
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
    
        const basePrice = productTmplId?.list_price || 0;
        const isBilateral = laterality === "bilateral";
        const totalBase = isBilateral ? basePrice * 2 : basePrice;
    
        const total = (totalBase + leftTotal + rightTotal) * quantityToMake;
    
        this.state.summary = result;
        this.state.priceSummary = {
            base: totalBase,
            left: leftTotal,
            right: rightTotal,
            shared: sharedTotal,
            total,
        };
    
        console.log("✅ Final summary:", result);
        console.log("💰 Price summary:", this.state.priceSummary);
    }
    
    

    printSummary() {
        const printContents = this.summaryWrapper.el?.outerHTML;
        if (!printContents) return;

        const win = window.open("", "_blank");
        win.document.write(`
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
        win.document.close();
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
};
