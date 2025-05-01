/** @odoo-module **/

/* eslint-disable sort-imports */

/**
 * Resolves the current order and line context for saving CPQ configurations.
 * 
 * ✅ Accepts virtual or missing `activeId` if creating (edit: false)
 * ❌ Throws error if editing (edit: true) but activeId is missing or virtual
 * 
 * Sources values from:
 *   - this.props.orderId / this.context.active_sale_order_id
 *   - this.props.activeId / this.context.active_id
 *   - this.props.record?.resId (fallback)
 *
 * Returns:
 *   {
 *     orderId: number | null,
 *     activeId: number | string | null,
 *     isVirtual: boolean
 *   }
 */


import { scrollTo } from "@web/core/utils/scrolling";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { Component, onWillStart, useEffect, useState, useSubEnv } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import ProductTmplAttrib from "./product_tmpl_attrib.esm";
import SummaryPanel from "./configurator_summary_panel.esm";
import { validateProps, cleanGhostRecords, nextTick, useDebouncedInput, debounce, safeMany2One, computeLocalCPQPriceBreakdown } from "./utils.esm";

export class ConfigureDialog extends Component {
    static template = "cpq.ConfigureDialogDialog";

    static components = { Dialog, ProductTmplAttrib, SummaryPanel };

    static props = {
        orderId: Number,
        productTemplateId: Number,
        productTemplate: { type: Object, optional: true },
        quantity: { type: Number, optional: true },          
        currencyId: { type: Number, optional: true },      
        soDate: { type: String, optional: true },             
        productUOMId: { type: Number, optional: true },
        pricelistId: { type: Number, optional: true },
        companyId: { type: Number, optional: true },
        cpqInitialConfig: { type: Object, optional: true },   
        record: { type: Object, optional: true },             
        context: { type: Object, optional: true, default: () => ({}) },
        edit: { type: Boolean, optional: true },             
        activeId: { type: [Number, String], optional: true },  
        save: { type: Function, optional: true },            
        close: Function,
        discard: Function,
    };
    
    setup() {
        super.setup();
        validateProps(this, ConfigureDialog.props);
        this.size = "xl";
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.dialogService = useService("dialog");
        this.actionService = useService("action");
        this.context = this.props.context || this.props.record?.model?.root?.context || {};
        this.quantity = this.props.quantity ?? 1;
        this.currencyId = this.props.currencyId ?? this.props.record?.data?.currency_id?.[0] ?? this.productTemplate?.currency_id?.[0] ?? 1;
        this.soDate = this.props.soDate || new Date().toISOString().split("T")[0];

        // Initial State
        this.state = useState({
            isLoading: false,
            isInitializing: true,
            valid: false,
            productTemplateId: this.props.productTemplateId, 
            productTemplate: null, 
            selected: {},
            quantityToMake: this.props.quantity || 1,
            totalPrice: 0,
            errors: {},
            ptalIds: [],
            priceSummary: { base: 0, extrasSubtotal: 0, total: 0 },
            laterality: "bilateral",
            split: false,
            expanded: true,
            showExtras: false,
            summary: [],
            toastMessage: null,
            undoCache: { left: null, right: null },
            // showPrintPreview: false,
        });
        
        this.orderId = this.props.orderId || this.context?.active_sale_order_id;
        this.activeId = this.context?.active_id || this.props.record?.resId;
        this.state.productTemplateId = this.props.productTemplateId;
        this.state.productTemplate = this.props.productTemplate || {}; // fallback

        this.state.priceBreakdown = {
            base: 0,
            extras: 0,
            discountPct: 0,
            subtotal: 0,
            quantity: this.state.quantityToMake,
            total: 0,
        };

        this.formatCurrency = (value) => {
            const number = typeof value === "number" ? value : parseFloat(value) || 0;
            return `$${number.toFixed(2)}`;
        };

        this.updatePricePreview = async () => {
            const productTemplateId = this.productTemplateId;
            if (!productTemplateId) {
                console.warn("⛔ Skipping price preview: productTemplateId is undefined.");
                return;
            }
            const combination = this._flattenCombination(this.state.selected);
            const contextPayload = {
                active_model: "sale.order.line",
                active_id: this.props.context?.active_id || this.props.record?.resId,
                active_sale_order_id: this.props.orderId,
                ...(this.props.context || {}),
            };
        
            try {
                const response = await this.rpc(`/cpq/${productTemplateId}/price_preview`, {
                    configuration: combination,
                    context: contextPayload,
                });
        
                if (response?.breakdown) {
                    this.state.priceBreakdown = response.breakdown;
                    return;
                }
            } catch (err) {
                console.warn("⚠️ Server-side price preview failed, using fallback:", err);
            }
        
            // 💡 Fallback to local estimate if server fails
            const base = this.productTemplate?.list_price || 0;
            const extras = this.summaryApi?.getSummaryState?.().priceSummary.extrasSubtotal || 0;
            const quantity = this.state.quantityToMake || 1;
            const discountFactor = 1.0;
        
            this.state.priceBreakdown = computeLocalCPQPriceBreakdown({
                basePrice: base,
                extras,
                discountFactor,
                quantity,
            });
        };

        this.debouncedInput = useDebouncedInput(250);
  
        this.onQuantityChange = this.debouncedInput((val) => {
            const parsed = parseInt(val, 10);
            const finalVal = isNaN(parsed) || parsed < 1 ? 1 : parsed;
            console.log("🔢 Debounced Quantity to Make:", finalVal);
            this.state.quantityToMake = finalVal;
        });

        this.onIncreaseQuantity = () => {
            this.state.quantityToMake += 1;
            // this.summaryApi?.recalculate();  
            this.summaryApi?.computeSummary?.();
            this.updatePricePreview();  // Optional: for real-time pricing refresh

        };
        
        this.onDecreaseQuantity = () => {
            if (this.state.quantityToMake > 1) {
                this.state.quantityToMake -= 1;
                // this.summaryApi?.recalculate();
                this.summaryApi?.computeSummary?.();
                this.updatePricePreview();  // Optional: for real-time pricing refresh

            }
        };

        this.registerSummaryPanel = api => { this.summaryApi = api; };
        // this.togglePrintPreview = () => { this.state.showPrintPreview = !this.state.showPrintPreview; };

        this.summaryKey = () => {
            try {
                return JSON.stringify(this.state.selected || {});
            } catch (e) {
                console.warn("⚠️ Failed to stringify selected:", e);
                return "invalid-key";
            }
        };

        useSubEnv({
            updateQuantity: this.onQuantityChange.bind(this),
            state: this.state,
            formatCurrency: this.formatCurrency,  // ✅ Expose it here
        });

        this.onLateralityChange = (ev) => {
            this.state.laterality = ev.target.value;
            this.state.split = false;
            this.state.selected = {};
        };
        
        useEffect(() => {
            console.log("🔁 useEffect triggered (selected, quantityToMake, laterality, split)");
            this._validate();
            this.summaryApi?.computeSummary?.();
            this.updatePricePreview();
            this._refreshHandler();
        }, () => [
            this.state.selected.left,
            this.state.selected.right,
            this.state.quantityToMake,
            this.state.laterality,
            this.state.split,
        ]);

        onWillStart(async () => {
            console.log("🧩 onWillStart props:", this.props);
            console.log("🧩 onWillStart context:", this.context);
            this.state.isInitializing = true;
        
            try {
                const loadedData = await this._loadData();
                this.title = this.props.edit
                    ? _t("Edit Configuration: %s", loadedData.product_tmpl_id.display_name)
                    : _t("Configure: %s", loadedData.product_tmpl_id.display_name);
        
                this.state.ptalIds = loadedData.ptal_ids;
                this.state.productTemplateId = loadedData.product_tmpl_id.id;
                this.state.productTemplate = loadedData.product_tmpl_id;
        
                // 🔍 Fallback if somehow productTemplate is still missing or invalid
                if (!this.state.productTemplate?.id && this.state.productTemplateId) {
                    const fallback = await this.orm.call("product.template", "read", [[this.state.productTemplateId], ["name", "uom_id", "currency_id", "list_price"]]);
                    this.state.productTemplate = fallback?.[0] || {};
                }
        
                const initialConfigRaw = this.props.cpqInitialConfig || this.props.context?.cpq_initial_config;
                if (initialConfigRaw) {
                    const parsed = typeof initialConfigRaw === "string" ? JSON.parse(initialConfigRaw) : initialConfigRaw;
                    this.state.selected = parsed.selected || {};
                    this.state.laterality = parsed.laterality || "bilateral";
                    this.state.split = parsed.split || false;
                    this.state.quantityToMake = parsed.quantity_to_make || 1;
        
                    this.initialState = {
                        laterality: this.state.laterality,
                        split: this.state.split,
                        selected: JSON.parse(JSON.stringify(this.state.selected)),
                        quantityToMake: this.state.quantityToMake,
                    };
                }
        
                await nextTick();
                if (Object.keys(this.state.selected).length > 0) {
                    console.warn("🧪 About to validate combination:", this._flattenCombination(this.state.selected));
                    await this._validate();
                    this.summaryApi?.computeSummary?.();
                    this.updatePricePreview();
                }
        
            } catch (error) {
                console.error("❌ Initialization error:", error);
                this.notification.add("Initialization failed. Please try again.", { type: "danger" });
            } finally {
                this.state.isInitializing = false;
            }
        });
        
        
        // onWillStart(async () => {
        //     console.log("🧩 onWillStart props:", this.props);
        //     console.log("🧩 onWillStart context:", this.context);
        //     this.state.isInitializing = true;
        //     try {
        //         const data = await this._loadData();
        //         this.title = this.props.edit
        //             ? _t("Edit Configuration: %s", data.product_tmpl_id.display_name)
        //             : _t("Configure: %s", data.product_tmpl_id.display_name);

        //         this.state.ptalIds = data.ptal_ids;
        //         this.state.productTemplateId = data.product_tmpl_id.id;
        //         this.state.productTemplate = data.product_tmpl_id;

        //         if (!this.state.productTemplate?.id && this.productTemplateId) {
        //             const data = await this.orm.call("product.template", "read", [[this.productTemplateId], ["name", "uom_id", "currency_id", "list_price"]]);
        //             this.state.productTemplate = data[0];
        //         }
                

        //         const initialConfigRaw = this.props.cpqInitialConfig || this.props.context?.cpq_initial_config;
        //         if (initialConfigRaw) {
        //             const parsed = typeof initialConfigRaw === "string" ? JSON.parse(initialConfigRaw) : initialConfigRaw;
        //             this.state.selected = parsed.selected || {};
        //             this.state.laterality = parsed.laterality || "bilateral";
        //             this.state.split = parsed.split || false;
        //             this.state.quantityToMake = parsed.quantity_to_make || 1;

        //             this.initialState = {
        //                 laterality: this.state.laterality,
        //                 split: this.state.split,
        //                 selected: JSON.parse(JSON.stringify(this.state.selected)),
        //                 quantityToMake: this.state.quantityToMake,
        //             };
        //         }

        //         await nextTick();
        //         if (Object.keys(this.state.selected).length > 0) {
        //             console.warn("🧪 About to validate combination:", this._flattenCombination(this.state.selected));
        //             await this._validate();
        //             this.summaryApi?.computeSummary?.();
        //             this.updatePricePreview();

        //         }

        //     } catch (error) {
        //         console.error("❌ Initialization error:", error);
        //         this.notification.add("Initialization failed. Please try again.", { type: "danger" });
        //     } finally {
        //         this.state.isInitializing = false;
        //     }
        // });

        this.onSplitToggle = async () => {
            const goingToShared = this.state.split;
            const goingToSplit = !this.state.split;

            const left = this.state.selected.left;
            const right = this.state.selected.right;
            const leftHasData = left && Object.keys(left).length > 0;
            const rightHasData = right && Object.keys(right).length > 0;

            if (goingToShared && (leftHasData || rightHasData)) {
                const confirmed = await this._showConfirmDialog(
                    "Switching to shared mode will erase left and right configurations. Continue?"
                );
                if (!confirmed) return;

                this.state.undoCache.left = JSON.parse(JSON.stringify(this.state.selected.left));
                this.state.undoCache.right = JSON.parse(JSON.stringify(this.state.selected.right));
                this._cleanSide("left");
                this._cleanSide("right");
            }

            if (goingToSplit && leftHasData && !rightHasData) {
                this.state.selected.right = JSON.parse(JSON.stringify(this.state.selected.left));
            }

            if (goingToSplit) {
                this.state.sharedBeforeSplit = JSON.parse(JSON.stringify(this.state.selected));
            }

            this.state.split = !this.state.split;
        };

        this.copyLeftToRight = () => {
            const left = this.state.selected.left;
            if (left && Object.keys(left).length > 0) {
                const validRightPtavIds = new Set(
                    this.state.ptalIds.flatMap((a) => a.ptav_ids.map((v) => v.id))
                );
                const filteredCopy = {};
                for (const [ptavId, value] of Object.entries(left)) {
                    if (validRightPtavIds.has(Number(ptavId))) {
                        filteredCopy[ptavId] = value;
                    }
                }
                if (Object.keys(filteredCopy).length > 0) {
                    this.state.selected.right = JSON.parse(JSON.stringify(filteredCopy));
                    this.notification.add("✅ Copied Left ➡️ Right", { type: "success" });
                } else {
                    this.notification.add("⚠️ No compatible attributes to copy Left ➡️ Right.", { type: "warning" });
                }
            } else {
                this.notification.add("⚠️ Left side has no data to copy.", { type: "warning" });
            }
        };

        this.copyRightToLeft = () => {
            const right = this.state.selected.right;
            if (right && Object.keys(right).length > 0) {
                const validLeftPtavIds = new Set(
                    this.state.ptalIds.flatMap((a) => a.ptav_ids.map((v) => v.id))
                );
                const filteredCopy = {};
                for (const [ptavId, value] of Object.entries(right)) {
                    if (validLeftPtavIds.has(Number(ptavId))) {
                        filteredCopy[ptavId] = value;
                    }
                }
                if (Object.keys(filteredCopy).length > 0) {
                    this.state.selected.left = JSON.parse(JSON.stringify(filteredCopy));
                    this.notification.add("✅ Copied Right ➡️ Left", { type: "success" });
                } else {
                    this.notification.add("⚠️ No compatible attributes to copy Right ➡️ Left.", { type: "warning" });
                }
            } else {
                this.notification.add("⚠️ Right side has no data to copy.", { type: "warning" });
            }
        };

        // Setup refresh debounce
        this._refreshHandler = debounce(() => {
            this.summaryApi?.computeSummary?.();
            this.updatePricePreview();
        }, 300);

        // Auto-refresh when quantity changes
        this._setupAutoRefresh = () => {
            useEffect(() => {
                this._refreshHandler();
            }, () => [this.state.quantityToMake]);
        };
        this._setupAutoRefresh();
  

    }

    _setupAutoRefresh() {
        useEffect(() => {
            this._refreshHandler();
        }, () => [ this.state.quantityToMake ]);
    }

    onQuantityChange(eventOrValue) {
        const value = eventOrValue?.target?.value ?? eventOrValue;
        const newQuantity = parseInt(value, 10) || 1;
        this.state.quantityToMake = newQuantity;
    
        console.log("🧩 Quantity updated to:", this.state.quantityToMake);
    
        this.summaryApi?.computeSummary?.();
        this.updatePricePreview();

    }
    
 
    increaseQuantity() {
        this.state.quantityToMake += 1;
    }
    decreaseQuantity() {
        if (this.state.quantityToMake > 1) {
            this.state.quantityToMake -= 1;
        }
    }

    //---------------------------------------------------------------------
    // ⚙️ Data Exchanges and Context-safe onCreate
    //---------------------------------------------------------------------


    async _loadData() {
        const productTemplateId = this.props.productTemplateId;
        console.log("🔍 productTemplateId received:", this.props.productTemplateId);

        if (!productTemplateId) {
            console.error("❌ Missing product template ID in _loadData()");
            throw new Error("Missing product template ID");
        }
        return this.rpc(`/cpq_product_configurator/${productTemplateId}/data`, {});
    }

    async _validate() {
        const productTemplateId = this.productTemplateId;
        if (!productTemplateId) {
            console.warn("⛔ Skipping validation: productTemplateId is undefined.");
            return;
        }
        const combination = this._flattenCombination(this.state.selected || {});
        if (!Object.keys(combination).length) {
            console.log("⏭️ Skipping validation — selected is empty.");
            return;
        }
    
        try {
            const res = await this.rpc(`/cpq/${this.productTemplateId}/validate`, {
                combination,
            });
            this.state.valid = res.valid;
            this.state.errors = res.errors;
        } catch (e) {
            this.state.valid = false;
            this.state.errors = { general: "Validation RPC error." };
        }
    }

    canCreate() { return this.state.valid; }

    onCreate = debounce(async () => {
        console.log("🧩 onCreate() running");
        console.log("🧩 props:", this.props);
        console.log("🧩 context:", this.context);
    
        if (this.state.isLoading) return;

        const { orderId, activeId, isVirtual } = this._resolveOrderAndLineContext();
        if (this.props.edit && (!activeId || isVirtual)) {
            console.warn("⛔ Cannot proceed: trying to edit without valid order line ID.");
            return;
        }

        if (!orderId) {
            this.notification.add("Missing order ID. Please reload the order.", { type: "danger" });
            return;
        }
    
        if (!activeId) {
            this.notification.add("Missing order line ID. Cannot continue.", { type: "danger" });
            return;
        }

        if (isVirtual) {
            this.notification.add("⚠️ You’re configuring a new product before saving the order.", {
                type: "warning",
                sticky: true,
            });
        }

        // Proceed even if `activeId` is virtual
        const productTemplate = this.productTemplate || this.props.productTemplate;
        const productTemplateId = productTemplate?.id || this.props.productTemplateId;
    
        if (!productTemplateId) {
            console.error("❌ Missing productTemplate. Aborting.");
            this.notification.add("Product template is missing or invalid.", { type: "danger" });
            return;
        }
    
        try {
            const confirmed = await this._showConfirmDialog("Save this configuration to the order?");
            if (!confirmed) return;

            this.state.isLoading = true;
            await this.env.services.ui.block();  
        
            // if (!this.state.valid) {
            //     this.notification.add("Please fix the validation errors before saving.", { type: "warning" });
            //     return;
            // }
    
            await this._validate();
            if (!this.state.valid) {
                this.notification.add("Please fix the validation errors before saving.", { type: "warning" });
                return;
            }
            await nextTick();
            this.summaryApi?.computeSummary?.();
            this.updatePricePreview();
    
            const summary = this.summaryApi?.getSummaryState?.() || {};

            const productUom = Array.isArray(productTemplate?.uom_id)
                ? productTemplate.uom_id[0]
                : productTemplate?.uom_id
                || this.props.record?.data?.product_uom?.[0]
                || this.props.productUOMId
                || null;

    
            // const productUom = Array.isArray(productTemplate?.uom_id)
            //     ? productTemplate.uom_id[0]
            //     : productTemplate?.uom_id || this.props.productUOMId || null;
    
            const config = {
                name: this.productTemplateName,
                laterality: this.state.laterality,
                split: this.state.split,
                selected: this.state.selected,
                quantity_to_make: this.state.quantityToMake,
                product_uom_qty: this.state.quantityToMake,
                product_uom: productUom,
                price_unit: this.state.priceBreakdown?.total / this.state.quantityToMake || 0,
                left_price: summary.left || 0,
                right_price: summary.right || 0,
                total_price: summary.total || 0,
                product_template_id: productTemplateId,
            };

            console.warn("🧪 Fallback chain: uom_id from props.record", this.props.record?.data?.product_uom);
            console.warn("🧪 Fallback chain: uom_id from productTemplate", productTemplate?.uom_id);
            console.warn("🧪 Final resolved product_uom:", productUom);

            if (!config.product_uom) {
                this.notification.add("Product UoM is missing. Cannot continue.", { type: "danger" });
                return;
            }
            
            const contextPayload = {
                active_model: "sale.order.line",
                active_id: activeId,
                active_sale_order_id: orderId,
                ...(this.context || {}),
            };
    
            console.log("🚀 Submitting CPQ config:", config);
            console.log("🧩 Context for RPC:", contextPayload);
    
            const response = await this.rpc(
                `/cpq_product_configurator/${productTemplateId}/configure`,
                { configuration: config, context: contextPayload }
            );
    
            console.log("✅ CPQ configure response:", response);
    
            if (response?.configuration) {
                this.notification.add("✅ Configuration successfully saved to order line.", { type: "success" });
    
                if (this.props.record?.load) {
                    await this.props.record.load();
                    this.pulseElement(".cpq-config-summary");
                    console.log("✅ Frontend record reloaded after configuration save");
                }
    
                this._redirectToOrder(orderId);
            } else {
                this.notification.add("Unexpected server response. Please try again.", { type: "danger" });
            }
    
        } catch (error) {
            console.error("❌ Failed to submit configuration:", error);
            this.notification.add("An error occurred while saving configuration.", { type: "danger" });
        } finally {
            this.state.isLoading = false;
            await this.env.services.ui.unblock();  // 🔓 Always unblock even on error
        }
    });
    
    _resolveOrderAndLineContext() {
        const context = this.context || {};
        const props = this.props || {};
    
        const orderId =
            this.orderId ||
            props.orderId ||
            context.active_sale_order_id ||
            context.sale_order_id ||
            props.record?.model?.root?.resId ||
            null;
    
        console.log("🧪 props.record:", props.record);
        console.log("🧪 props.record?.resId:", props.record?.resId, typeof props.record?.resId);

        // let activeId =
        //     context.active_id ||
        //     props.activeId ||
        //     this.activeId ||
        //     (props.record?.resId !== false ? props.record?.resId : null);

        // let activeId =
        //     context.active_id ||
        //     props.activeId ||  
        //     this.activeId ||
        //     (props.record?.resId !== false ? props.record?.resId : null);

        let activeId =
            props.activeId ||  // ✅ Trust this first if explicitly passed
            context.active_id ||
            (props.record?.resId && typeof props.record.resId === "number" ? props.record.resId : null);

        // const isVirtual = typeof activeId === "string" && activeId.startsWith("virtual_");
        const isVirtual = !activeId || (typeof activeId === "string" && activeId.startsWith("virtual_"));

        // 🔍 Log for diagnostics
        console.warn("🧩 [_resolveOrderAndLineContext] Inputs:", { orderId, activeId, isVirtual });
        console.log("props.record?.resId:", props.record?.resId, typeof props.record?.resId);
        console.log("props.orderId:", props.orderId);
        console.log("props.activeId:", props.activeId);
        console.log("props.record?.resId:", props.record?.resId);
        console.log("context.active_sale_order_id:", context.active_sale_order_id);
        console.log("context.active_id:", context.active_id);
        console.log("→ resolved orderId:", orderId);
        console.log("→ resolved activeId:", activeId);
    
        // 🚫 Only warn if we're editing (not creating) and activeId is truly missing
        if (!orderId) {
            console.warn("⚠️ _resolveOrderAndLineContext: Missing orderId");
        }
        if (!activeId) {
            console.warn("⚠️ _resolveOrderAndLineContext: Missing activeId entirely");
        }

        // if (this.props.edit && isVirtual) {
        //     this.notification.add("Missing order line ID. Cannot continue.", { type: "danger" });
        //     throw new Error("Missing order line ID in edit mode.");
        // }

        if (this.props.edit) {
            if (!activeId || isVirtual) {
                this.notification.add("⚠️ This configuration must be saved before editing.", { type: "danger" });
                throw new Error("Missing order line ID in edit mode.");
            }
        }

        return { orderId, activeId, isVirtual };
    }
    
    
    async _addOrUpdateSelected(sideOrId, attributeId, valueIdOrPtavId, customValue) {
        const isSplit = typeof sideOrId === "string" && ["left", "right"].includes(sideOrId);
        const side = isSplit ? sideOrId : null;
        const attrId = isSplit ? attributeId : sideOrId;
        const ptavId = parseInt(valueIdOrPtavId, 10);
    
        if (isNaN(ptavId)) {
            console.warn("❌ Invalid PTAV ID:", valueIdOrPtavId);
            return;
        }

        console.groupCollapsed("🔄 _addOrUpdateSelected");
        console.log("sideOrId:", sideOrId);
        console.log("attributeId:", attributeId);
        console.log("valueIdOrPtavId:", valueIdOrPtavId);
        console.log("customValue:", customValue);
        console.log("→ resolved side:", side);
        console.log("→ resolved attrId:", attrId);
        console.log("→ resolved ptavId:", ptavId);
    
        const attr = this.state.ptalIds.find((a) => a.id === attrId);
        if (!attr) {
            console.warn("⚠️ No attribute found for ID:", attrId);
            console.groupEnd();
            return;
        }
    
        const ptav = attr.ptav_ids.find((v) => v.id === ptavId);
        if (!ptav) {
            console.warn(`⚠️ PTAV ID ${ptavId} not found in attribute "${attr.name}"`);
            console.groupEnd();
            return;
        }
    
        // const value = ptav.is_custom && customValue !== undefined ? customValue : ptav.name;
        const value = ptav.is_custom && customValue !== undefined ? customValue : ptavId;
        const newSelected = JSON.parse(JSON.stringify(this.state.selected));
    
        if (isSplit) {
            newSelected[side] = newSelected[side] || {};
            for (const v of attr.ptav_ids) {
                delete newSelected[side][v.id];
            }
            newSelected[side][ptavId] = value;
            console.log(`🦶 Updated ${side} side for "${attr.name}":`, newSelected[side]);
        } else {
            for (const v of attr.ptav_ids) {
                delete newSelected[v.id];
            }
            newSelected[ptavId] = value;
            console.log(`🧩 Updated shared selection for "${attr.name}":`, newSelected);
        }
    
        this.state.selected = newSelected;

        console.log("🧠 New selected state:", JSON.stringify(this.state.selected, null, 2));
        console.groupEnd();
    
        await nextTick();
        await new Promise((resolve) => setTimeout(resolve, 0));

        console.log("✅ Running validation and summary update...");
        this._validate();
        this.summaryApi?.computeSummary?.();
        this.updatePricePreview();
    }

    async _showConfirmDialog(message) {
        return new Promise(resolve => {
            this.dialogService.add(ConfirmationDialog, {
                title: _t("Please Confirm"),
                body: message,
                confirmLabel: _t("Yes, continue"),
                cancelLabel: _t("Cancel"),
                confirm: () => resolve(true),
                cancel: () => resolve(false),
            });
        });
    }

    _handleSharedSelect(attributeId, ev) {
        const ptavId = parseInt(ev.target.value, 10);
        if (isNaN(ptavId)) {
            console.warn("❌ Skipping update: Invalid ptavId from value:", ev.target.value);
            return;
        }
        this._addOrUpdateSelected(attributeId, null, ptavId);  // ✅ Correct param order
    }

    _cleanSide(side) {
        if (this.state.selected?.[side]) {
            delete this.state.selected[side];
        }
    }

    _restoreUndoCache() {
        if (this.state.undoCache.left) {
            this.state.selected.left = JSON.parse(JSON.stringify(this.state.undoCache.left));
        }
        if (this.state.undoCache.right) {
            this.state.selected.right = JSON.parse(JSON.stringify(this.state.undoCache.right));
        }
        this._validate();
    }

    _hasUnsavedChanges() {
        if (!this.initialState) return false;
        
        const current = {
            laterality: this.state.laterality,
            split: this.state.split,
            selected: this.state.selected,
            quantityToMake: this.state.quantityToMake,
        };
        
        return JSON.stringify(current) !== JSON.stringify(this.initialState);
    }

    // Used to flatten split selections for backend calls.
    _flattenCombination(selected) {
        const result = {};
        if (!selected) return result;
    
        if (selected.left || selected.right) {
            for (const side of ["left", "right"]) {
                for (const [key, val] of Object.entries(selected[side] || {})) {
                    const ptavId = parseInt(key, 10);
                    if (!isNaN(ptavId)) result[ptavId] = val;  // ✅ preserve the value (may be string)
                }
            }
        } else {
            for (const [key, val] of Object.entries(selected || {})) {
                const ptavId = parseInt(key, 10);
                if (!isNaN(ptavId)) result[ptavId] = val;  // ✅ preserve the value
            }
        }
    
        return result;
    }
    
    async _applyConfigurationResult(result) {
        console.log("🧩 Applying configuration result:", result);
    
        const activeId = result?.sale_order_line_id || this.context?.active_id;
        const orderId = result?.sale_order_id || this.props.orderId;
    
        if (!activeId || !orderId) {
            this.notification.add("Missing order line or order context. Please reload the page.", { type: "danger" });
            return false;
        }
    
        try {
            await this.env.services.ui.block();
    
            const staleResId = this.props.record?.resId;
            if (staleResId && staleResId !== activeId) {
                console.log(`🧹 Cleaning up stale native line: ${staleResId}`);
                await this.orm.call("sale.order.line", "unlink", [[staleResId]]);
            }
    
            try {
                await cleanGhostRecords(this.props.record, activeId);
            } catch (error) {
                console.warn("⚠️ cleanGhostRecords failed:", error);
            }

            // ✅ Extra safety: ensure no virtual lines remain
            const orderModel = this.props.record?.model?.root;
            if (orderModel?.data?.order_line?.records) {
                orderModel.data.order_line.records = orderModel.data.order_line.records.filter(
                    (line) => line.resId === activeId
                );
                orderModel.data.order_line.leaveEditMode?.();
                console.log("✅ Final frontend cleanup: Cleared virtual lines from order model");
            }

            this.notification.add("✅ Configuration successfully saved to order line.", { type: "success" });
            this.pulseElement(".cpq-config-summary");
            this.pulseElement(`[data-id="${activeId}"]`);
    
            const lineEl = document.querySelector(`[data-id="${activeId}"]`);
            if (lineEl) {
                lineEl.scrollIntoView({ behavior: "smooth", block: "center" });
                lineEl.classList.add("highlight-success");
                setTimeout(() => lineEl.classList.remove("highlight-success"), 1500);
            }

            console.log("🚀 Redirecting to Sale Order:", orderId);
            await this.env.services.action.doAction({
                type: "ir.actions.act_window",
                res_model: "sale.order",
                res_id: orderId,
                views: [[false, "form"]],
                target: "current",
            });
            await this.env.services.notification.add("✅ Order line updated!", { type: "success" });
            return true;
        } catch (error) {
            console.error("❌ Failed to apply configuration result:", error);
            this.notification.add("An error occurred while updating the order line.", { type: "danger" });
            return false;
        } finally {
            await this.env.services.ui.unblock();
        }
    }
    
    async onClose() {
        await this._closeDialog();
    }

    async _closeDialog(force = false) {
        if (!force && this._hasUnsavedChanges?.()) {
            const confirmed = await this._showConfirmDialog("⚠️ You have unsaved configuration changes. Exit anyway?");
            if (!confirmed) return;
        }

        this.state.ptalIds = [];
        this.state.selected = {};
        this.state.productTemplateId = null;  
        this.state.valid = false;
        this.state.errors = {};
        this.state.productTemplate = {};
        this.context = {};
        this.props.context = {};
        // await this.props.record?.discard?.();  // revert virtual changes

        this.props.discard?.();
        this.props.close?.();
    }

    async resetOnlySelections() {
        if (!this.initialState) {
            this.notification.add("No initial state available.", { type: "warning" });
            return;
        }
        
        const confirmed = await this._showConfirmDialog("Reset only your attribute selections? Quantity and laterality will stay.");
        if (!confirmed) {
            return;
        }
        
        this.state.isLoading = true;
        
        try {
            console.log("🔄 Resetting selections only (keeping quantity and laterality).");
        
            this.state.selected = JSON.parse(JSON.stringify(this.initialState.selected));
        
            await nextTick();
        
            await this._validate();
            this.summaryApi?.computeSummary?.();
            this.updatePricePreview();

            this.notification.add("✅ Attribute selections reset.", { type: "success" });
        } catch (error) {
            console.error("❌ Failed to reset selections:", error);
            this.notification.add("An error occurred while resetting selections.", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    async resetToDefaults() {
        if (!this.initialState) {
            this.notification.add("No initial configuration to reset to.", { type: "warning" });
            return;
        }
        
        const confirmed = await this._showConfirmDialog("Reset configuration to the original defaults?");
        if (!confirmed) {
            return;
        }
        
        this.state.isLoading = true;
        
        try {
            console.log("🔄 Resetting to initial state:", this.initialState);
        
            this.state.laterality = this.initialState.laterality;
            this.state.split = this.initialState.split;
            this.state.quantityToMake = this.initialState.quantityToMake;
            this.state.selected = JSON.parse(JSON.stringify(this.initialState.selected));
        
            await nextTick();
            await this._validate();
            this.summaryApi?.computeSummary?.();
            this.updatePricePreview();

            this.notification.add("✅ Configuration reset to defaults.", { type: "success" });
            this.pulseElement(".cpq-config-summary");
            this.pulseElement(".pricing-summary"); // Optional: if you want price totals to animate
            this.summaryApi?.showToast?.("✅ Configuration reset!");
        } catch (error) {
            console.error("❌ Failed to reset configuration:", error);
            this.notification.add("An error occurred while resetting.", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
        
    }

    //---------------------------------------------------------------------
    // ⚙️ Getters and Setters
    //---------------------------------------------------------------------

    get selectionCount() {
        const left = Object.keys(this.state.selected.left || {}).length;
        const right = Object.keys(this.state.selected.right || {}).length;
        const shared = Object.keys(this.state.selected || {}).length;
        return this.state.split ? left + right : shared;
    }
        
    get isInitializing() {
        return this.state.isInitializing;
    }
        
    get isDisabled() {
        return this.state.isLoading || this.state.isInitializing;
    }

    get productTemplate() {
        return this.state?.productTemplate || this.props?.productTemplate || {};
    }
    
    get productTemplateId() {
        return this.state?.productTemplateId || this.props?.productTemplateId || null;
    }
    
    get productTemplateName() {
        return this.productTemplate.display_name || "Configured Product";
    }
    
    
    pulseElement(selector) {
        const element = document.querySelector(selector);
        if (!element) return;

        element.classList.remove("highlight-success");
        void element.offsetWidth;
        element.classList.add("highlight-success");
    }

    // Redirect to sale order
    async _redirectToOrder(orderId) {
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "sale.order",
            res_id: orderId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

export function ConfigureDialogAction(env, action) {
    const context = action.context || {};
    console.log("🧪 [ConfigureDialogAction] context:", context);
    console.log("🧪 activeId (from context):", context.active_id);
    // console.log("🧪 isEdit:", isEdit);
    // console.log("🧪 isVirtual:", isVirtual);

    const rawTmpl = context.product_tmpl_id || context.product_template_id || context.cpq_product_template_id;
    const productTemplate = typeof rawTmpl === "object" ? rawTmpl : undefined;
    const productTemplateId = typeof rawTmpl === "object" ? rawTmpl.id : rawTmpl;

    const orderLineData = env.services.model?.root?.data?.order_line;
    const orderId = context.orderId || context.active_sale_order_id || context.sale_order_id;
    let activeId = context.active_id;

    // Fallback: resolve from sale.order's first line if needed
    if (!activeId && context.active_model === "sale.order") {
        activeId = orderLineData?.length ? orderLineData[0]?.resId : null;
    }

    const currencyId = context.currencyId || context.currency_id;
    const soDate = context.soDate || context.so_date || new Date().toISOString().split("T")[0];
    const quantity = typeof context.quantity === "number" ? context.quantity : 1;
    const isVirtual = typeof activeId === "string" && activeId.startsWith("virtual_");
    const isEdit = context.edit === true && typeof activeId === "number" && activeId > 0;

    console.log("🧪 isEdit:", isEdit);
    console.log("🧪 isVirtual:", isVirtual);

    // Reject editing virtual lines
    if (isEdit && (!activeId || isVirtual)) {
        env.services.notification.add(
            _t("This configuration must be saved before editing."),
            { type: "warning" }
        );
        return;
    }

    const missingProps = [];
    if (!productTemplateId) missingProps.push("productTemplateId");
    if (!orderId) missingProps.push("orderId");
    if (!currencyId) missingProps.push("currencyId");
    if (!soDate) missingProps.push("soDate");

    if (missingProps.length) {
        console.error("❌ Missing required fields for ConfigureDialog:", missingProps);
        env.services.notification.add(
            _t("Cannot open configurator. Missing: ") + missingProps.join(", "),
            { type: "danger" }
        );
        return;
    }

    const fullContext = {
        ...context,
        active_model: "sale.order.line",
        active_id: activeId,
        active_sale_order_id: orderId,
    };

    // Optional: clean up frontend lines if resId present
    if (activeId && orderLineData?.records) {
        orderLineData.records = orderLineData.records.filter(line => line.resId === activeId);
        orderLineData.leaveEditMode?.();
        console.log("✅ Cleaned frontend order line data");
    }

    const dialogProps = {
        productTemplateId,
        // productTemplate: typeof rawTmpl === "object" ? rawTmpl : null,
        productTemplate, // only if real object
        orderId,
        currencyId,
        soDate,
        quantity,
        context: fullContext,
        edit: isEdit,
        save: async (res) => {
            if (!isEdit || (activeId && !isVirtual)) {
                try {
                    const values = {
                        product_id: res.configuration.product_id,
                        cpq_configuration_json: res.configuration.cpq_configuration_json,
                        cpq_configuration_summary: res.configuration.cpq_configuration_summary,
                        product_uom_qty: res.configuration.quantity_to_make,
                        name: res.configuration.name,
                    };

                    console.log("📝 Writing configuration to sale.order.line:", values);

                    await env.services.orm.call("sale.order.line", "onchange", [activeId, values]);
                    await env.services.orm.call("sale.order.line", "write", [activeId, values]);

                    env.services.notification.add(_t("✅ Configuration applied successfully."), { type: "success" });

                    env.services.action.doAction({
                        type: "ir.actions.act_window",
                        res_model: "sale.order",
                        res_id: orderId,
                        views: [[false, "form"]],
                        target: "current",
                    });
                } catch (error) {
                    console.error("❌ Failed to write configuration:", error);
                    env.services.notification.add(_t("Failed to apply configuration to the order line."), { type: "danger" });
                }
            } else {
                env.services.action.doAction({ type: "ir.actions.act_window_close" });
            }
        },
        close: () => env.services.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sale.order",
            res_id: orderId,
            views: [[false, "form"]],
            target: "current",
        }),
        discard: () => env.services.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sale.order",
            res_id: orderId,
            views: [[false, "form"]],
            target: "current",
        }),
    };

    console.log("🧩 Opening ConfigureDialog with props:", dialogProps);
    env.services.dialog.add(ConfigureDialog, dialogProps);
}

registry.category("actions").add("cpq.ConfigureDialogAction", ConfigureDialogAction);
