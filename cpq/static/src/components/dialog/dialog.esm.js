/** @odoo-module **/
/* eslint-disable sort-imports */
import { scrollTo } from "@web/core/utils/scrolling";
import {_t} from "@web/core/l10n/translation";
import { escape } from "@web/core/utils/strings";
import {Dialog} from "@web/core/dialog/dialog";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import {Component, onWillStart, onWillUpdateProps, useEffect, useRef, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {WarningDialog} from "@web/core/errors/error_dialogs";
import ProductTmplAttrib from "./product_tmpl_attrib.esm";
import SummaryPanel from "./configurator_summary_panel.esm";
import { validateProps, applyProduct, nextTick, useDebouncedInput} from "./utils.esm";  


export class ConfigureDialog extends Component {
    static template = "cpq.ConfigureDialogDialog";

    static components = {
        Dialog, 
        ProductTmplAttrib,
        SummaryPanel,
    };

    static props = {
        orderId: { type: Number },
        productTmplId: Number,
        quantity: Number,
        currencyId: Number,
        soDate: String,
        productUOMId: { type: Number, optional: true },
        pricelistId: { type: Number, optional: true },
        companyId: { type: Number, optional: true },
        edit: Boolean,
        save: Function,
        close: Function,
        discard: Function,
    };
    
    
    
    setup() {
        super.setup();

        // Dev-time prop check
        validateProps(this, {
            orderId: { type: "number", optional: true },
            productTmplId: "number",
            save: "function",
            close: "function",
            edit: "boolean",
            discard: { type: "function", optional: true },
        });
         

        this.size = "xl";
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.dialogService = useService("dialog"); 
        this.initialState = null;
        this.state = useState({
            ptalIds: [],
            selected: {},
            productTmplId: null,
            valid: false,
            errors: {},
            laterality: "bilateral",
            split: false,
            quantityToMake: 1,
            undoCache: {
                left: null,
                right: null,
            },
            isLoading: false, 
            isInitializing: true,
        });
        
        this.debouncedInput = useDebouncedInput(250);

        this.onQuantityChange = this.debouncedInput((val) => {
            const parsed = parseInt(val, 10);
            const finalVal = isNaN(parsed) || parsed < 1 ? 1 : parsed;
            console.log("🔢 Debounced Quantity to Make:", finalVal);
            this.state.quantityToMake = finalVal;
        });

        this.summaryApi = null;

        this.registerSummaryPanel = (api) => {
            if (!api?.getSummaryState) {
                console.warn("⚠️ Summary API missing required methods.");
            }
            this.summaryApi = api;
        };


        this.summaryKey = () => {
            try {
                return JSON.stringify(this.state.selected || {});
            } catch (e) {
                console.warn("⚠️ Failed to stringify selected:", e);
                return "invalid-key";
            }
        };
        
        // 🧠 Reactively recompute summary whenever left/right selection changes
        useEffect(() => {
            console.log("🔁 useEffect triggered (selected, quantityToMake, laterality, split)");
            console.log("📦 quantityToMake in useEffect:", this.state.quantityToMake);
            this.computeSummary?.();
        }, () => [
            this.state.selected.left,
            this.state.selected.right,
            this.state.quantityToMake,
            this.state.laterality,
            this.state.split,
        ]);
        
        this.onLateralityChange = (ev) => {
            this.state.laterality = ev.target.value;
            this.state.split = false;
            this.state.selected = {};
        };

        onWillStart(async () => {
            try {
                this.state.isInitializing = true;
        
                const data = await this._loadData();
                this.title = this.env.config?.context?.cpq_initial_config
                    ? _t("Edit Configuration: %s", data.product_tmpl_id.display_name)
                    : _t("Configure: %s", data.product_tmpl_id.display_name);
        
                this.state.ptalIds = data.ptal_ids;
                this.state.productTmplId = data.product_tmpl_id;
        
                // const initialConfigRaw = this.env.config?.context?.cpq_initial_config;

                const initialConfigRaw = this.props.cpqInitialConfig || this.env.config?.context?.cpq_initial_config;

        
                if (initialConfigRaw) {
                    try {
                        const parsed = typeof initialConfigRaw === "string"
                            ? JSON.parse(initialConfigRaw)
                            : initialConfigRaw;
        
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
        
                        console.log("🧩 Loaded initial config into state:", this.initialState);
                    } catch (e) {
                        console.warn("⚠️ Failed to parse cpq_initial_config:", e);
                    }
                }
        
                // ✅ Wait for reactivity flush
                await nextTick();
                await new Promise(resolve => setTimeout(resolve, 0));
        
                // ✅ Avoid double validation - skip if no selection
                if (Object.keys(this.state.selected).length > 0) {
                    await this._validate();
                    this.computeSummary?.();
                }
        
            } catch (error) {
                console.error("❌ Error during onWillStart initialization:", error);
                this.notification.add("Failed to initialize configurator. Please try again.", { type: "danger" });
            } finally {
                this.state.isInitializing = false;
            }
        });

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
                console.log("🧪 User confirmed:", confirmed);
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
    }

    //--------------------------------------------------------------------------
    // Data Exchanges
    //--------------------------------------------------------------------------

    async _loadData() {
        return this.rpc(`/cpq/${this.props.productTmplId}/data`, {});
    }

    canCreate() {
        if (!this.state.ptalIds) {
            return false;
        }

        return this.state.valid;
    }

    preparePayload() {
        const summary = this.summaryApi?.getSummaryState?.() || {};
        const name = this.productTemplateName;
    
        const config = {
            name,
            laterality: this.state.laterality,
            split: this.state.split,
            selected: this.state.selected,
            quantity_to_make: this.state.quantityToMake,
            left_price: summary.left || 0,
            right_price: summary.right || 0,
            total_price: summary.total || 0,
        };
    
        console.log("🧩 Prepared config payload:", config);
        return config;
    }
    
    async onCreate() {
        if (this.state.isLoading) return;
    
        this.state.isLoading = true;
        const confirmed = await this._showConfirmDialog("Save this configuration to the order?");
        if (!confirmed) {
            this.state.isLoading = false;
            return;
        }
    
        await this._validate();
    
        if (!this.state.valid) {
            this.notification.add("Please fix the validation errors before saving.", { type: "warning" });
            this.state.isLoading = false;
            return;
        }
        try {
            // ✅ Force recompute summary before capturing state
            this.computeSummary?.();
            await nextTick();
            await new Promise(resolve => setTimeout(resolve, 0));
        
            // ✅ Force SummaryPanel to recompute
            if (this.summaryApi?.computeSummary) {
                this.summaryApi.computeSummary();
                await nextTick();
                await new Promise(resolve => setTimeout(resolve, 0));
            }
        
            const summary = this.summaryApi;
            const name = this.productTemplateName;

            // 🧩 Defensive check to ensure summaryApi exists
            if (!summary) {
                console.warn("⚠️ Summary API is not available. Pricing totals will be zero.");
            }

            const leftTotal = summary?.getLeftTotal?.() || 0;
            const rightTotal = summary?.getRightTotal?.() || 0;
            const combinedTotal = summary?.getCombinedTotal?.() || 0;

            console.log("🧩 Summary totals:", {
                leftTotal,
                rightTotal,
                combinedTotal,
            });

            const config = this.preparePayload();

            console.log("🚀 Prepared config for backend:", config);

            const res = await this.rpc(`/cpq/${this.props.productTmplId}/configure`, { configuration: config });
        
            if (res?.configuration) {
                console.log("✅ Configuration saved successfully:", res);
        
                const success = await this._applyConfigurationResult(res);
                if (success) {
                    this._closeDialog();
        
                    if (res.sale_order_id) {
                        this.env.services.action.doAction({
                            type: "ir.actions.act_window",
                            res_model: "sale.order",
                            res_id: res.sale_order_id,
                            views: [[false, "form"]],
                            target: "current",
                        });
                    }
                }
            } else {
                this.notification.add("Unexpected response from server. Please try again.", { type: "danger" });
            }
        } catch (error) {
            console.error("❌ Failed to submit configuration:", error);
            this.notification.add("An error occurred while saving configuration.", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
        
    }
    
    async _applyConfigurationResult(result) {
        if (!this.props.record) {
            console.warn("⚠️ No record prop passed to ConfigureDialog.");
            this.notification.add("No record available to update the order line.", { type: "warning" });
            return false;
        }
    
        try {
            await applyProduct(this.props.record, result);
            console.log("✅ Order line updated successfully.");
            this.notification.add("Configuration applied to the order line successfully.", { type: "success" });
    
            // 🧩 Debug this!
            console.log("🧩 Debug Navigation Check: ", {
                record: this.props.record,
                recordResId: this.props.record?.resId,
                recordId: this.props.record?.id,
            });

            if (this.env.services.action && result?.sale_order_id) {
                console.log("🚀 Navigating to sale order form view:", result.sale_order_id);
                this.env.services.action.doAction({
                    type: 'ir.actions.act_window',
                    res_model: 'sale.order',
                    res_id: result.sale_order_id,
                    views: [[false, 'form']],
                    target: 'current',
                });
            }
            
    
            // if (this.env.services.action && result?.sale_order_line_id) {
            //     console.log("🚀 Navigating to sale order line form view:", result.sale_order_line_id);
            //     this.env.services.action.doAction({
            //         type: 'ir.actions.act_window',
            //         res_model: 'sale.order.line',
            //         res_id: result.sale_order_line_id,
            //         views: [[false, 'form']],
            //         target: 'current',
            //     });
            // }
        
            return true;
    
        } catch (error) {
            console.error("❌ Failed to update order line with configuration result:", error);
            this.notification.add(
                "An error occurred while updating the order line. Please check your configuration.",
                { type: "danger" }
            );
            return false;
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
    
        // Clean state
        this.state.ptalIds = [];
        this.state.selected = {};
        this.state.productTmplId = null;
        this.state.valid = false;
        this.state.errors = {};
    
        // Trigger discard if available
        this.props.discard?.();
    
        // Close dialog
        this.props.close?.();
    }
    
    async _validate() {
        if (!this.state.selected) {
            console.warn("⚠️ No selection found. Skipping validation.");
            return;
        }
    
        const productTmplId = this.props.productTmplId;
    
        try {
            const res = await this.rpc(`/cpq/${productTmplId}/validate`, {
                combination: this.state.selected,
            });
    
            this.state.valid = res.valid;
            this.state.errors = res.errors;
    
            if (res.valid) {
                console.log("✅ Configuration is valid.");
            } else {
                console.warn("⚠️ Configuration is invalid:", res.errors);
            }
    
        } catch (error) {
            console.error("🚨 Validation RPC failed:", error);
    
            this.state.valid = false;
            this.state.errors = {
                general: "Validation failed due to a server error.",
            };
    
            if (this.notification) {
                this.notification.add(
                    "⚠️ Failed to validate configuration. Please try again.",
                    { type: "danger" }
                );
            }
        }
    }

    async _addOrUpdateSelected(sideOrId, attributeId, valueIdOrPtavId, customValue) {
        // const isSplit = ["left", "right"].includes(sideOrId);
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
    
        console.log(`✅ Attribute matched: "${attr.name}"`);
        console.log(`↳ PTAV selected: "${ptav.name}" (custom? ${ptav.is_custom})`);
    
        // Clone current selection for reactivity
        const newSelected = JSON.parse(JSON.stringify(this.state.selected));
    
        if (isSplit) {
            newSelected[side] = newSelected[side] || {};
            for (const v of attr.ptav_ids) {
                delete newSelected[side][v.id];
            }
            newSelected[side][ptavId] = ptav.is_custom && customValue !== undefined ? customValue : ptav.name;
            console.log(`🦶 Updated ${side} side for "${attr.name}":`, newSelected[side]);
        } else {
            for (const v of attr.ptav_ids) {
                delete newSelected[v.id];
            }
            newSelected[ptavId] = ptav.is_custom && customValue !== undefined ? customValue : ptav.name;
            console.log(`🧩 Updated shared selection for "${attr.name}":`, newSelected);
        }
    
        this.state.selected = newSelected;
    
        console.log("🧠 New selected state:", JSON.stringify(this.state.selected, null, 2));
        console.groupEnd();
    
        // Wait for reactivity flush
        await nextTick();
        await new Promise((resolve) => setTimeout(resolve, 0));
    
        console.log("✅ Running validation and summary update...");
        this._validate();
        this.computeSummary?.();
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
            this.computeSummary?.();
    
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
            this.computeSummary?.();
    
            this.notification.add("✅ Attribute selections reset.", { type: "success" });
        } catch (error) {
            console.error("❌ Failed to reset selections:", error);
            this.notification.add("An error occurred while resetting selections.", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    async _showConfirmDialog(message) {
        return new Promise((resolve) => {
            console.log("📣 Opening confirmation dialog:", message); // ✅ Log the intent
            this.dialogService.add(ConfirmationDialog, {
                title: _t("Please Confirm"),
                body: message,
                confirmLabel: _t("Yes, continue"),
                cancelLabel: _t("Cancel"),
                confirm: () => {
                    console.log("✅ User clicked confirm in dialog");
                    resolve(true);
                },
                cancel: () => {
                    console.log("🚫 User clicked cancel in dialog");
                    resolve(false);
                },
            });
        });
    }
    

    //----------------------------------------------------------------------
    // Getters
    //----------------------------------------------------------------------
    
    get isInitializing() {
        return this.state.isInitializing || !this.summaryApi;
    }
    
    get isDisabled() {
        return !this.summaryApi || this.state.isLoading;
    }

    get productTemplateId() {
        const val = this.state.productTmplId;
        return typeof val === "number" ? val : val?.id;
    }
    
    get productTemplateName() {
        const val = this.state.productTmplId;
        return typeof val === "object" ? val.display_name : "Configured Product";
    }

    pulseElement(selector) {
        const element = document.querySelector(selector);
        if (!element) return;
    
        element.classList.remove('highlight-success');
        void element.offsetWidth; // ✅ Force reflow to restart animation
        element.classList.add('highlight-success');
    }

}

export function ConfigureDialogAction(env, action) {
    const context = action.context;

    const productTmplId =
        context.cpq_product_template_id ||
        context.product_template_id || 
        context.active_id;

    env.services.dialog.add(ConfigureDialog, {
        productTmplId,
        // productTmplId: context.cpq_product_template_id || context.active_id,
        
        edit: true,
        cpqInitialConfig: context.cpq_initial_config || null, // ✅ pass to dialog
        save: async (res) => {
            if (!productTmplId) {
                console.warn("⚠️ No product template ID passed to ConfigureDialogAction context:", context);
            }
            
            if (context.active_model === "sale.order.line" && context.active_id) {
                try {
                    const values = {
                        product_id: res.configuration.product_id,
                        cpq_configuration_json: res.configuration.cpq_configuration_json,
                        cpq_configuration_summary: res.configuration.cpq_configuration_summary,
                        product_uom_qty: res.configuration.quantity_to_make,
                        name: res.configuration.name,
                    };

                    console.log("📝 Writing configuration to sale.order.line:", values);
                    await env.services.orm.call("sale.order.line", "onchange", [context.active_id], values);

                    await env.services.orm.call(
                        "sale.order.line", 
                        "write", 
                        [context.active_id, values]
                    );
                    
                    env.services.action.doAction({
                        type: "ir.actions.act_window",
                        res_model: "sale.order.line",
                        res_id: context.active_id,
                        views: [[false, "form"]],
                        target: "current",
                    });
                    
                } catch (error) {
                    console.error("❌ Failed to write configuration to sale.order.line:", error);
                    env.services.notification.add(
                        "Failed to apply configuration to the order line.",
                        { type: "danger" }
                    );
                }
            } else {
                env.services.action.doAction({ type: "ir.actions.act_window_close" });
            }
        },
        close: () => env.services.action.doAction({ type: "ir.actions.act_window_close" }),
        discard: () => env.services.action.doAction({ type: "ir.actions.act_window_close" }),
    });
}

registry.category("actions").add("cpq.ConfigureDialogAction", ConfigureDialogAction);

 