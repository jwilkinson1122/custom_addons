/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUpdateProps } from "@odoo/owl";

export default class ConfiguratorSummaryPanel extends Component {
    setup() {
        this.summaryWrapper = useRef("summaryWrapper");

        this.state = useState({
            summary: [],
            priceSummary: { left: 0, right: 0, total: 0 }, 
            expanded: false,
            height: 0,
        });

        onMounted(() => {
            console.log("📌 SummaryPanel mounted");
            this.adjustHeight();
        });

        onWillUpdateProps(() => {
            console.log("🌀 DOM patched → computing summary...");
            this.computeSummary();
        });

        this.computeSummary();
    }

    get visibleAttributes() {
        const MAX_VISIBLE = 5;
        return this.state.expanded ? this.props.ptalIds : this.props.ptalIds.slice(0, MAX_VISIBLE);
    }

    toggleExpand() {
        this.state.expanded = !this.state.expanded;
        this.adjustHeight();
    }

    adjustHeight() {
        setTimeout(() => {
            const el = this.summaryWrapper.el;
            if (!el) return;

            if (this.state.expanded) {
                el.style.height = "auto";
                const fullHeight = el.scrollHeight;
                el.style.height = "0px";
                void el.offsetHeight;
                this.state.height = fullHeight;
            } else {
                this.state.height = 0;
            }
        }, 0);
    }

    computeSummary() {
        console.log("🧠 Computing summary:");
        const { ptalIds = [], selected = {}, laterality, split } = this.props;
    
        const selectedLeft = selected.left || {};
        const selectedRight = selected.right || {};
        const sharedSelected = selected;
    
        let leftTotal = 0;
        let rightTotal = 0;
    
        const result = ptalIds.map((attr) => {
            let left = "-", right = "-", shared = "-";
            let priceExtra = 0;
    
            if (laterality === "bilateral" && split) {
                left = selectedLeft[attr.id] ?? "-";
                right = selectedRight[attr.id] ?? "-";
    
                const leftPTAV = attr.ptav_ids.find(v => v.id === parseInt(Object.keys(selectedLeft).find(id => parseInt(id) === attr.id)));
                const rightPTAV = attr.ptav_ids.find(v => v.id === parseInt(Object.keys(selectedRight).find(id => parseInt(id) === attr.id)));
    
                if (leftPTAV?.price_extra) leftTotal += leftPTAV.price_extra;
                if (rightPTAV?.price_extra) rightTotal += rightPTAV.price_extra;
    
                console.log(`↔️ [${attr.name}] Left: ${left} | Right: ${right}`);
            } else {
                shared = sharedSelected[attr.id] ?? "-";
    
                const sharedPTAV = attr.ptav_ids.find(v => v.id === parseInt(Object.keys(sharedSelected).find(id => parseInt(id) === attr.id)));
    
                if (sharedPTAV?.price_extra) {
                    priceExtra = sharedPTAV.price_extra;
                    leftTotal += priceExtra;
                }
    
                console.log(`🧩 [${attr.name}] Shared: ${shared}`);
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

// ConfiguratorSummaryPanel.props = {
//     ptalIds: Array,
//     selected: Object,
//     laterality: String,
//     split: Boolean,
//     productTmplId: Number,
// };


