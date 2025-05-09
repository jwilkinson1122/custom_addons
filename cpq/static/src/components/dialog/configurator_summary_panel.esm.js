/** @odoo-module **/
// import { html } from "@odoo/owl";

import { Component, useState, useRef, onMounted, onWillUpdateProps, onWillUnmount, html } from "@odoo/owl";
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
            console.log("Debounced recompute summary");
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
                console.log("Initial ptalIds detected, computing summary...");
                this.computeSummary();
            }

            this.adjustHeight();
        });

        onWillUpdateProps((nextProps) => {
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

    renderGroup(group) {
        const selected = this.props.selected || {};
        const isSplit = this.props.split;
        const laterality = this.props.laterality;
    
        const renderChild = (attr) => {
            if (attr.is_group) {
                return this.renderGroup(attr);  // recursion for nested groups
            }
    
            const values = attr.values || [];
            const findSelectedVal = (dict) => values.find(val => dict?.[val.id]);
    
            const selLeft = findSelectedVal(selected.left || {});
            const selRight = findSelectedVal(selected.right || {});
            const selShared = findSelectedVal(selected);
    
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
        // const laterality = this.props.laterality;
    
        const renderChild = (attr) => {
            if (attr.is_group) {
                return this.renderGroupHtmlString(attr);
            }
    
            const values = attr.values || [];
            const findSelectedVal = (dict) => values.find(val => dict?.[val.id]);
    
            const selLeft = findSelectedVal(selected.left || {});
            const selRight = findSelectedVal(selected.right || {});
            const selShared = findSelectedVal(selected);
    
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
    

    // Handles shared and split + proper bilateral pricing logic
    computeSummary() {
        console.log("Computing summary...");
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
    
        const result = allAttributes.map((attr, index) => {
            if (!attr || attr.is_group) return null;
    
            if (!attr.name || !Array.isArray(attr.values) || attr.values.length === 0) {
                console.warn("Skipping invalid attribute:", attr);
                return null;
            }
    
            const values = attr.values;
    
            const getSelectedValue = (values, selectedDict) => {
                for (const v of values) {
                    if (selectedDict.hasOwnProperty(v.id)) {
                        return {
                            ...v,
                            ...(selectedDict[v.id] || {}),
                        };
                    }
                }
                return null;
            };
    
            const formatValue = (val) => {
                if (!val) return "-";
                if (val.is_custom && val.value) return `✍️ ${val.value}`;
                return val.name || "-";
            };
    
            let left = "-", right = "-", shared = "-", priceExtra = 0;
            let leftVal = null, rightVal = null, sharedVal = null;
    
            if (isSplit) {
                leftVal = getSelectedValue(values, selectedLeft);
                rightVal = getSelectedValue(values, selectedRight);
    
                if (!leftVal && !rightVal) return null;  // Skip if nothing selected
    
                left = formatValue(leftVal);
                right = formatValue(rightVal);
    
                const leftExtra = (leftVal?.price_extra || 0) * quantityToMake;
                const rightExtra = (rightVal?.price_extra || 0) * quantityToMake;
    
                leftTotal += leftExtra;
                rightTotal += rightExtra;
                priceExtra = leftExtra + rightExtra;
            } else {
                sharedVal = getSelectedValue(values, selected);
                if (!sharedVal) return null;  // Skip if nothing selected
    
                shared = formatValue(sharedVal);
                const sharedExtra = (sharedVal?.price_extra || 0) * quantityToMake;
    
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
                note: leftVal?.note || rightVal?.note || sharedVal?.note || "",
            };
        }).filter(Boolean);  // Remove nulls (skipped unselected or invalid)
    
        const basePrice = productTemplate?.list_price || 0;
        const baseMultiplier = laterality === "bilateral" ? 2 : 1;
        const totalBase = basePrice * baseMultiplier * quantityToMake;
        const totalExtras = leftTotal + rightTotal;
        const total = totalBase + totalExtras;
    
        this.state.summary = result;
    
        if (typeof this.props.matrixPriceTotal === "number") {
            const matrixTotal = this.props.matrixPriceTotal;
            this.state.priceSummary = {
                base: 0,
                left: 0,
                right: 0,
                total: matrixTotal,
                extrasSubtotal: 0,
            };
            console.log("Matrix price override applied:", matrixTotal);
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
    
        console.log("Final summary computed:", result);
    }
    

    // computeSummary() {
    //     console.log("Computing summary...");
    //     const {
    //         ptalIds = [],
    //         selected = {},
    //         laterality,
    //         split,
    //         productTemplate,
    //         quantityToMake = 1,
    //     } = this.props;
    
    //     const selectedLeft = selected.left || {};
    //     const selectedRight = selected.right || {};
    //     const isSplit = laterality === "bilateral" && split;
    
    //     let leftTotal = 0;
    //     let rightTotal = 0;
    
    //     const result = ptalIds.map((attr, index) => {
    //         if (!attr || !attr.name || !Array.isArray(attr.ptav_ids)) {
    //             return {
    //                 key: `summary-invalid-${index}`,
    //                 label: "Invalid Attribute",
    //                 left: "-",
    //                 right: "-",
    //                 shared: "-",
    //                 priceExtra: 0,
    //             };
    //         }
    
    //         const ptavs = attr.ptav_ids;
    //         const getSelectedPtav = (ptavs, selectedDict) =>
    //             ptavs.find((ptav) => ptav.id in selectedDict) || null;
    
    //         let left = "-", right = "-", shared = "-", priceExtra = 0;
    
    //         if (isSplit) {
    //             const leftPtav = getSelectedPtav(ptavs, selectedLeft);
    //             const rightPtav = getSelectedPtav(ptavs, selectedRight);
    
    //             left = leftPtav?.name || "-";
    //             right = rightPtav?.name || "-";
    
    //             const leftExtra = (leftPtav?.price_extra || 0) * quantityToMake;
    //             const rightExtra = (rightPtav?.price_extra || 0) * quantityToMake;
    
    //             leftTotal += leftExtra;
    //             rightTotal += rightExtra;
    //             priceExtra = leftExtra + rightExtra;
    
    //         } else {
    //             const sharedPtav = getSelectedPtav(ptavs, selected);
    //             shared = sharedPtav?.name || "-";
    //             const sharedExtra = (sharedPtav?.price_extra || 0) * quantityToMake;
    
    //             if (laterality === "left") {
    //                 left = shared;
    //                 leftTotal += sharedExtra;
    //                 priceExtra = sharedExtra;
    //             } else if (laterality === "right") {
    //                 right = shared;
    //                 rightTotal += sharedExtra;
    //                 priceExtra = sharedExtra;
    //             } else if (laterality === "bilateral") {
    //                 left = shared;
    //                 right = shared;
    //                 const bilateralExtra = sharedExtra * 2;
    //                 leftTotal += bilateralExtra / 2;
    //                 rightTotal += bilateralExtra / 2;
    //                 priceExtra = bilateralExtra;
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
    

    //     const basePrice = productTemplate?.list_price || 0;
    //     // const basePrice = this.props.productTemplate?.list_price || 0;
    //     const baseMultiplier = laterality === "bilateral" ? 2 : 1;
    //     const totalBase = basePrice * baseMultiplier * quantityToMake;
    //     const totalExtras = leftTotal + rightTotal;
    //     const total = totalBase + totalExtras;
    
    //     this.state.summary = result;

    //     // After computing totalBase, totalExtras, total...

    //     // Use matrix price if provided via props
    //     if (typeof this.props.matrixPriceTotal === "number") {
    //         const matrixTotal = this.props.matrixPriceTotal;
        
    //         this.state.priceSummary = {
    //             base: 0,
    //             left: 0,
    //             right: 0,
    //             total: matrixTotal,
    //             extrasSubtotal: 0,
    //         };
        
    //         console.log("Matrix price override applied:", matrixTotal);
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
    
    //     console.log("Final summary computed:", result);
    // }
    

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
        const summaryRows = this.state.summary || [];
    
        const rows = summaryRows.map(s => {
            const sharedOrLeft = this.props.split ? s.left : s.shared ?? s.left ?? "-";
            const right = s.right ?? "-";
            const match = s.left === s.right ? "[OK]" : "❌";
    
            return `<tr>
                <td>${s.label}</td>
                <td>${sharedOrLeft}</td>
                ${this.props.split ? `<td>${right}</td><td>${match}</td>` : ""}
                <td>$${(s.priceExtra || 0).toFixed(2)}</td>
            </tr>`;
        }).join("");
    
        const hasVisibleRows = rows.trim().length > 0;
    
        const fallbackMessage = `<tr><td colspan="${this.props.split ? 4 : 2}" style="text-align: center; font-style: italic; color: #888;">
            🟡 No configuration options selected yet.
        </td></tr>`;
    
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
                            <th>${this.props.split ? "Left" : "Value"}</th>
                            ${this.props.split ? "<th>Right</th><th>Match</th>" : ""}
                            <th>Price</th>
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
            </body>
            </html>
        `;
    }
    
    // _generatePrintHtml() {
    //     const pb = this.state.priceSummary || {};
    //     const rows = this.state.summary.map(s => {
    //         const sharedOrLeft = this.props.split ? s.left : s.shared ?? s.left ?? "-";
    //         const right = s.right ?? "-";
    //         const match = s.left === s.right ? "[OK]" : "❌";
        
    //         return `<tr>
    //             <td>${s.label}</td>
    //             <td>${sharedOrLeft}</td>
    //             ${this.props.split ? `<td>${right}</td><td>${match}</td>` : ""}
    //             <td>$${(s.priceExtra || 0).toFixed(2)}</td>
    //         </tr>`;
    //     }).join("");
    //     const matrixBadge = this.props.matrixOverrideActive
    //     ? `<p><span class="badge bg-warning text-dark">Price overridden by matrix</span></p>`
    //     : "";
    //     let groupSection = "";
    //     if (this.props.ptalIds?.some(g => g.is_group)) {
    //         const topLevelGroups = this.props.ptalIds.filter(g => g.is_group);
    //         groupSection = `<hr/><h3>Structured Group View</h3>` +
    //             topLevelGroups.map(g => this._generateGroupHtml(g)).join("");
    //     }
    //     return `
    //         <html>
    //         <head>
    //             <title>Configuration Summary</title>
    //             <style>
    //                 body { font-family: sans-serif; margin: 20px; }
    //                 table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    //                 th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
    //                 th { background: #f0f0f0; }
    //                 .totals { font-weight: bold; }
    //                 .badge { display: inline-block; padding: 5px 10px; background: #ffc107; color: #000; border-radius: 4px; font-size: 0.9em; }
    //             </style>
    //         </head>
    //         <body>
    //             <h2>Product Configuration Summary</h2>
    //             <p><b>Product:</b> ${this.productTemplate?.display_name || "-"}</p>
    //             <p><b>Quantity:</b> ${this.props.quantityToMake}</p>
    //             <table>
    //                 <thead>
    //                     <tr>
    //                         <th>Attribute</th>
    //                         <th>${this.props.split ? "Left" : "Value"}</th>
    //                         ${this.props.split ? "<th>Right</th><th>Match</th>" : ""}
    //                         <th>Price</th>
    //                     </tr>
    //                 </thead>
    //                 <tbody>${rows}</tbody>
    //             </table>
    //             <div class="totals">
    //                 <p>💸 Base Price: $${pb.base?.toFixed(2) || "0.00"}</p>
    //                 <p>➕ Extras: $${pb.extrasSubtotal?.toFixed(2) || "0.00"}</p>
    //                 <p>Subtotal: $${pb.subtotal?.toFixed(2) || "0.00"}</p>
    //                 <p>× Quantity: ${pb.quantity || this.props.quantityToMake}</p>
    //                 <p>📊 Final Total: <b>$${pb.total?.toFixed(2) || "0.00"}</b></p>
    //                 ${matrixBadge}
    //                 ${groupSection}
    //             </div>
    //         </body>
    //         </html>
    //     `;
    // }

    
    

    // _generateGroupHtml(group) {
    //     const selected = this.props.selected || {};
    //     const isSplit = this.props.split;
    //     const laterality = this.props.laterality;
    //     const quantityToMake = this.props.quantityToMake || 1;
    
    //     const renderChild = (attr) => {
    //         if (attr.is_group) {
    //             return this._generateGroupHtml(attr);  
    //         }
    
    //         const values = attr.values || [];
    //         const findSelectedVal = (dict) => values.find(v => dict[v.id]);
    //         const selLeft = findSelectedVal(selected.left || {});
    //         const selRight = findSelectedVal(selected.right || {});
    //         const selShared = findSelectedVal(selected);
    
    //         let left = "-", right = "-", shared = "-";
    //         if (laterality === "bilateral" && isSplit) {
    //             left = selLeft?.name || "-";
    //             right = selRight?.name || "-";
    //         } else {
    //             shared = selShared?.name || "-";
    //         }
    
    //         return `<div style="margin-left: 20px;">
    //             <strong>${attr.name}</strong>: ${isSplit ? `L: ${left}, R: ${right}` : shared}
    //         </div>`;
    //     };
    
    //     const children = (group.children || []).map(renderChild).join("");
    
    //     return `<div style="margin-top: 12px;">
    //         <h4 style="margin-bottom: 6px;">${group.name}</h4>
    //         ${children}
    //     </div>`;
    // }

    _generateGroupHtml(group) {
        const selected = this.props.selected || {};
        const isSplit = this.props.split;
        const laterality = this.props.laterality;
        const quantityToMake = this.props.quantityToMake || 1;
    
        const renderChild = (attr) => {
            if (attr.is_group) {
                const rendered = this._generateGroupHtml(attr);
                return rendered ? rendered : "";
            }
    
            const values = attr.values || [];
    
            const findSelectedVal = (dict) => {
                return values.find(v => dict?.[v.id]);
            };
    
            const selLeft = findSelectedVal(selected.left || {});
            const selRight = findSelectedVal(selected.right || {});
            const selShared = findSelectedVal(selected);
    
            const shouldShow = isSplit
                ? (selLeft || selRight)
                : selShared;
    
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
    productTemplate: Object,
    quantityToMake: Number,
    register: Function,
    matrixPriceTotal: { type: Number, optional: true },
    matrixOverrideActive: { type: Boolean, optional: true },  
};
