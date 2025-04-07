/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUpdateProps, onWillUnmount } from "@odoo/owl";

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
                base: 0,
                left: 0,
                right: 0,
                shared: 0,
                total: 0,
                extrasSubtotal: 0,
            },
            expanded: true,
            height: 0,
            showExtras: false,
            quantityToMake: props.quantityToMake || 1,
            toastMessage: "",
        });

        this.toggleExtras = () => {
            this.state.showExtras = !this.state.showExtras;
        };

        // onMounted(() => {
        //     console.log("📌 SummaryPanel mounted");

        //     if (props.registerApi) {
        //         props.registerApi({
        //             showToast: this.showToast.bind(this),
        //         });
        //     }

        //     this.adjustHeight();
        // });

        onMounted(() => {
            console.log("📌 SummaryPanel mounted");

            if (this.props.registerApi) {
                this.props.registerApi({
                    showToast: this.showToast.bind(this),
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
            
        
            // if (this.props.registerApi) {
            //     this.props.registerApi({
            //         showToast: this.showToast.bind(this),
            //         getSummaryState: () => ({
            //             selections: this.state.summary,
            //             priceSummary: this.state.priceSummary,
            //             left: this.state.priceSummary.left,
            //             right: this.state.priceSummary.right,
            //             total: this.state.priceSummary.total,
            //         }),
            //         getLeftTotal: () => {
            //             const val = this.state.priceSummary.left || 0;
            //             console.log("💰 getLeftTotal:", val);
            //             return val;
            //         },
            //         getRightTotal: () => {
            //             const val = this.state.priceSummary.right || 0;
            //             console.log("💰 getRightTotal:", val);
            //             return val;
            //         },
            //         getCombinedTotal: () => {
            //             const val = this.state.priceSummary.total || 0;
            //             console.log("💰 getCombinedTotal:", val);
            //             return val;
            //         },
            //     });
            // }
        
            this.adjustHeight();
        });
        

        onWillUpdateProps((nextProps) => {
            const quantityChanged = nextProps.quantityToMake !== this.state.quantityToMake;

            if (quantityChanged) {
                console.log("🔄 Quantity changed from props:", nextProps.quantityToMake);
                this.state.quantityToMake = nextProps.quantityToMake;
            }

            requestAnimationFrame(() => {
                this._preserveScroll(() => this.computeSummary());
            });
        });

        // ✅ Add unmount cleanup
        onWillUnmount(() => {
            clearTimeout(this._heightTimeout);
            clearTimeout(this._toastTimeout);
            this.toastQueue = [];
        });

        this.computeSummary();
        console.log("🧠 Initial computeSummary:", this.state.quantityToMake);
    }

    showToast(message) {
        this.toastQueue.push(message);

        // If already displaying, let it finish
        if (this._toastTimeout) return;

        const showNextToast = () => {
            if (this.toastQueue.length === 0) {
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

    adjustHeight() {
        clearTimeout(this._heightTimeout);
        this._heightTimeout = setTimeout(() => {
            const el = this.summaryWrapper?.el;
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
        }, 20);
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

        const getSelectedPtav = (ptavs, selectedDict) => {
            return ptavs.find(ptav => Object.prototype.hasOwnProperty.call(selectedDict, ptav.id)) || null;
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

                const leftExtra = (leftPtav?.price_extra || 0) * quantityToMake;
                const rightExtra = (rightPtav?.price_extra || 0) * quantityToMake;

                leftTotal += leftExtra;
                rightTotal += rightExtra;
                priceExtra = leftExtra + rightExtra;
            } else {
                const sharedPtav = getSelectedPtav(ptavs, selected);
                shared = sharedPtav?.name || "-";
                const sharedExtra = sharedPtav?.price_extra || 0;

                const extraAmount = sharedExtra * quantityToMake;

                switch (laterality) {
                    case "left":
                        left = shared;
                        leftTotal += extraAmount;
                        priceExtra = extraAmount;
                        break;
                    case "right":
                        right = shared;
                        rightTotal += extraAmount;
                        priceExtra = extraAmount;
                        break;
                    case "bilateral":
                        left = shared;
                        right = shared;
                        const bilateralExtra = sharedExtra * 2 * quantityToMake;
                        leftTotal += bilateralExtra / 2;
                        rightTotal += bilateralExtra / 2;
                        priceExtra = bilateralExtra;
                        break;
                    default:
                        break;
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
        const isBilateral = laterality === "bilateral";
        const totalBase = (isBilateral ? basePrice * 2 : basePrice) * quantityToMake;

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

        console.log("✅ Final summary:", result);
        console.log("📦 Extras Subtotal:", totalExtras);
        console.log("💰 Total:", total);

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
        doc.close();

        win.focus();
        win.print();

        // ✅ Auto-close clean up
        win.onafterprint = () => win.close();
    }

    pulseElement(selector) {
        const element = document.querySelector(selector);
        if (!element) return;
    
        element.classList.remove('highlight-success');
        void element.offsetWidth; // Force reflow to restart animation
        element.classList.add('highlight-success');
    }
    
}

// Component Metadata
ConfiguratorSummaryPanel.template = "cpq.ConfiguratorSummaryPanel";

ConfiguratorSummaryPanel.props = {
    ptalIds: Array,
    selected: Object,
    laterality: String,
    split: Boolean,
    productTmplId: Object,
    quantityToMake: Number,
    registerApi: Function,
};
