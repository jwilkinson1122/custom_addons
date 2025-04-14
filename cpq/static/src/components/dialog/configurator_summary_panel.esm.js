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

        // 🔥 Register external API if provided
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

    computeSummary() {
        console.log("🧠 Computing summary...");
        const {
            ptalIds = [],
            selected = {},
            laterality,
            split,
            productTmplId,
        } = this.props;

        const selectedLeft = selected.left || {};
        const selectedRight = selected.right || {};
        const isSplit = laterality === "bilateral" && split;
        const quantityToMake = this.state.quantityToMake || 1;

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
            const getSelectedPtav = (ptavs, selectedDict) => ptavs.find(ptav => selectedDict[ptav.id]) || null;

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

        const previousTotal = this.state.priceSummary.total;

        const basePrice = productTmplId?.list_price || 0;
        const totalBase = (laterality === "bilateral" ? basePrice * 2 : basePrice) * quantityToMake;
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

        if (previousTotal !== total) {
            this.pulseElement(".pricing-summary");
        }
    }

    printSummary() {
        const printContents = this.summaryWrapper?.el?.outerHTML;
        if (!printContents) return;

        const win = window.open("", "_blank");
        if (!win) {
            console.warn("🚫 Failed to open print window.");
            return;
        }

        const doc = win.document;

        doc.open();
        doc.write(`<!DOCTYPE html><html><head><title>Configuration Summary</title></head><body>${printContents}</body></html>`);
        doc.close();

        win.focus();
        win.print();

        win.onafterprint = () => win.close();
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
    productTmplId: Object,
    quantityToMake: Number,
    register: Function,
};
