/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUpdateProps } from "@odoo/owl";

export default class ConfiguratorSummaryPanel extends Component {
    setup() {
        this.summaryWrapper = useRef("summaryWrapper");

        this.state = useState({
            summary: [],
            priceSummary: { left: 0, right: 0, total: 0 },
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

    computeSummary() {
        console.log("🧠 Computing summary...");
        const { ptalIds = [], selected = {}, laterality, split } = this.props;
    
        const selectedLeft = selected.left || {};
        const selectedRight = selected.right || {};
        const isSplit = laterality === "bilateral" && split;
    
        let leftTotal = 0;
        let rightTotal = 0;
    
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
    
                leftTotal += leftPtav?.price_extra || 0;
                rightTotal += rightPtav?.price_extra || 0;
            } else {
                const sharedPtav = getSelectedPtav(ptavs, selected);
                shared = sharedPtav?.name || "-";
                priceExtra = sharedPtav?.price_extra || 0;
    
                // Apply shared selection to both sides if not in split mode
                if (laterality === "left") {
                    left = shared;
                    leftTotal += priceExtra;
                } else if (laterality === "right") {
                    right = shared;
                    rightTotal += priceExtra;
                } else if (laterality === "bilateral" && !split) {
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
    
        this.state.summary = result;
        this.state.priceSummary = {
            left: leftTotal,
            right: rightTotal,
            total: leftTotal + rightTotal,
        };
    
        console.log("✅ Final summary:", result);
        console.log("💰 Price summary:", this.state.priceSummary);
    }
    
    
    
    // computeSummary() {
    //     console.log("🧠 Computing summary...");
    //     const { ptalIds = [], selected = {}, laterality, split } = this.props;
    
    //     const selectedLeft = selected.left || {};
    //     const selectedRight = selected.right || {};
    //     const sharedSelected = selected;
    
    //     console.log("📦 selected:", JSON.stringify(selected));
    //     console.log("🧩 selected raw:", sharedSelected);
    //     console.log("📦 selected.left:", JSON.stringify(selectedLeft));
    //     console.log("🧩 selected.left raw:", selectedLeft);
    //     console.log("📦 selected.right:", JSON.stringify(selectedRight));
    //     console.log("🧩 selected.right raw:", selectedRight);
    
    //     let leftTotal = 0;
    //     let rightTotal = 0;
    
    //     const getSelectedPtav = (ptavs, selectedDict, side) => {
    //         for (const ptav of ptavs) {
    //             if (Object.prototype.hasOwnProperty.call(selectedDict, ptav.id)) {
    //                 console.log(`✅ Found PTAV match for ${side} → ${ptav.name} (ID ${ptav.id})`);
    //                 return ptav;
    //             }
    //         }
    //         console.warn(`❌ No PTAV match found for ${side}`);
    //         return null;
    //     };
        
    
    //     const result = ptalIds.map((attr, index) => {
    //         if (!attr || !attr.name || !Array.isArray(attr.ptav_ids)) {
    //             console.warn(`⚠️ Skipping invalid attribute at index ${index}`, attr);
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
    //         console.log(`🔎 Attribute: ${attr.name} (ID ${attr.id}) → PTAVs:`, ptavs);
        
    //         console.log(`🧪 [DEBUG] Attribute "${attr.name}" selections:`);
    //         console.log(`  left selected keys:`, Object.keys(selectedLeft));
    //         console.log(`  right selected keys:`, Object.keys(selectedRight));
    //         console.log(`  PTAV ids:`, ptavs.map((p) => p.id));
        
    //         let left = "-", right = "-", shared = "-";
    //         let priceExtra = 0;
        
    //         if (laterality === "bilateral" && split) {
    //             const leftPtav = getSelectedPtav(ptavs, selectedLeft, "left");
    //             const rightPtav = getSelectedPtav(ptavs, selectedRight, "right");
        
    //             left = leftPtav?.name || "-";
    //             right = rightPtav?.name || "-";
        
    //             leftTotal += leftPtav?.price_extra || 0;
    //             rightTotal += rightPtav?.price_extra || 0;
    //         } else {
    //             const sharedPtav = getSelectedPtav(ptavs, sharedSelected, "shared");
        
    //             shared = sharedPtav?.name || "-";
    //             priceExtra = sharedPtav?.price_extra || 0;
        
    //             leftTotal += priceExtra;
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
    
    //     this.state.summary = result;
    //     this.state.priceSummary = {
    //         left: leftTotal,
    //         right: rightTotal,
    //         total: leftTotal + rightTotal,
    //     };
    //     console.log("🔍 Summary Check:", JSON.stringify(this.state.summary, null, 2));
    
    //     console.log("✅ Final summary:", result);
    //     console.log("💰 Price summary:", this.state.priceSummary);
    // }
    
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
};
