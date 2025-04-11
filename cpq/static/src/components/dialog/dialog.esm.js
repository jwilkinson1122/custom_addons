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
        // 🧩 Core context props
        orderId: Number,
        productTmplId: Number,
        quantity: Number,
        currencyId: Number,
        soDate: String,
        // 🧩 Optional contextual props
        productUOMId: { type: Number, optional: true },
        pricelistId: { type: Number, optional: true },
        companyId: { type: [Number, undefined], optional: true },
        // 🧩 Optional runtime data
        cpqInitialConfig: { type: Object, optional: true },
        record: { type: Object, optional: true },
        context: { type: Object, optional: true, default: () => ({}) },
        // 🧩 Dialog mode
        edit: Boolean,
        // 🧩 Lifecycle hooks
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
        this.initialState = null;
        this.summaryApi = null;
        // ✅ Resolve context from props, fallback to record model, or default to empty object
        this.context = this.props.context || this.props.record?.model?.root?.context || {};
        // this.context = this._resolveContext();
        this.state = useState({
            isLoading: false,
            isInitializing: true,
            valid: false,
            productTmplId: this.props.productTmplId,
            selected: {},
            quantityToMake: 1,
            errors: {},
            ptalIds: [],
            priceSummary: {
                base: 0,
                extrasSubtotal: 0,
                total: 0,
            },
            laterality: "bilateral",
            split: false,
            expanded: true,
            showExtras: false,
            summary: [],
            toastMessage: null,
            undoCache: { left: null, right: null },
        });

        // ✅ Debounced input for quantity field
        this.debouncedInput = useDebouncedInput(250);

        this.onQuantityChange = this.debouncedInput((val) => {
            const parsed = parseInt(val, 10);
            this.state.quantityToMake = isNaN(parsed) || parsed < 1 ? 1 : parsed;
        });

        // ✅ Summary panel API registration
        this.registerSummaryPanel = (api) => {
            this.summaryApi = api;
        };

        // ✅ Dynamic summary key (prevents stale updates)
        this.summaryKey = () => {
            try {
                return JSON.stringify(this.state.selected || {});
            } catch (e) {
                console.warn("⚠️ Failed to stringify selected:", e);
                return "invalid-key";
            }
        };

        // ✅ Quick laterality mode switch
        this.onLateralityChange = (ev) => {
            this.state.laterality = ev.target.value;
            this.state.split = false;
            this.state.selected = {};
        };

        // ✅ Effect: auto recompute on selection / quantity changes
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

        // ✅ Lifecycle on load
        onWillStart(async () => {
            this.state.isInitializing = true;
            try {
                const data = await this._loadData();
                this.title = this.props.edit
                    ? _t("Edit Configuration: %s", data.product_tmpl_id.display_name)
                    : _t("Configure: %s", data.product_tmpl_id.display_name);
                
                this.state.ptalIds = data.ptal_ids;
                this.state.productTmplId = data.product_tmpl_id;

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
                    await this._validate();
                    this.computeSummary?.();
                }

            } catch (error) {
                console.error("❌ Initialization error:", error);
                this.notification.add("Initialization failed. Please try again.", { type: "danger" });
            } finally {
                this.state.isInitializing = false;
            }
        });

        // ✅ Initialize compute summary immediately (if needed)
        this.computeSummary?.();

        // ✅ Split mode toggle allows for left/right configurations
        // ✅ Shared mode toggle allows for shared configurations
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

        // copy left configuration to right
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
        // copy right configuration to left
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

    // 📦 Load initial data
    async _loadData() {
        const productTmplId = this.props.productTmplId?.id || this.props.productTmplId;
    
        if (!productTmplId) {
            this.notification.add("Missing product template ID.", { type: "danger" });
            throw new Error("Missing productTmplId");
        }
    
        return this.rpc(`/cpq/${productTmplId}/data`, {});
    }

    canCreate() {
        return this.state.valid;
    }

    async onCreate() {
        console.log("🧩 onCreate() running");
        console.log("🧩 onCreate() props:", this.props);
        console.log("🧩 onCreate() context:", this.props.context);
    
        const activeId = this.props.context?.active_id || this.props.record?.resId;
        const orderId = this.props.orderId;
        // const orderId = this.props.orderId || this.props.record?.data?.order_id?.[0];
    
        console.log("🧩 onCreate() active_id:", activeId, "orderId:", orderId);
    
        if (!activeId || !orderId) {
            this.notification.add("Missing order context. Please reload the order.", { type: "danger" });
            return;
        }
    
        if (this.state.isLoading) {
            console.warn("🚧 Configuration already saving. Skipping duplicate submit.");
            return;
        }
        this.state.isLoading = true;
    
        try {
            // Confirm before proceeding
            const confirmed = await this._showConfirmDialog("Save this configuration to the order?");
            if (!confirmed) {
                this.state.isLoading = false;
                return;
            }
    
            // Validate before submission
            if (!this.state.valid) {
                this.notification.add("Please fix the validation errors before saving.", { type: "warning" });
                this.state.isLoading = false;
                return;
            }
    
            // Validate state & recompute summary
            await this._validate();
            this.computeSummary?.();
            await nextTick();
    
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
    
            const contextPayload = {
                active_model: "sale.order.line",
                active_id: activeId,
                active_sale_order_id: orderId,
                ...(this.props.context || {}),
            };
    
            console.log("🚀 Submitting CPQ config:", config);
            console.log("🧩 Context for RPC:", contextPayload);
    
            // Call backend route
            const response = await this.rpc(
                `/cpq/${this.props.productTmplId}/configure`,
                { configuration: config },
                { context: contextPayload }
            );
    
            console.log("✅ CPQ configure response:", response);
    
            if (response?.sale_order_line_id) {
                // Pulse UX for created/updated line
                this._pulseLine(response.sale_order_line_id);
            }
    
            if (response?.configuration) {
                const success = await this._applyConfigurationResult(response);
                if (success) {
                    this.notification.add("✅ Configuration successfully saved to order line.", { type: "success" });
                    this._closeDialog();
                } else {
                    this.notification.add("Configuration saved, but could not apply result.", { type: "warning" });
                }
            } else {
                this.notification.add("Unexpected server response. Please try again.", { type: "danger" });
            }
    
        } catch (error) {
            console.error("❌ Failed to submit configuration:", error);
            this.notification.add("An error occurred while saving configuration.", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }
    
    async _applyConfigurationResult(result) {
        console.log("🧩 Applying configuration result:", result);
        const activeId = result?.sale_order_line_id || this.props.context?.active_id;
        // const activeId = result?.sale_order_line_id || this.props.context?.active_id || this.props.record?.resId;
        const orderId = result?.sale_order_id || this.props.orderId;
        // const orderId = result?.sale_order_id || this.props.orderId || this.props.record?.data?.order_id?.[0];
        if (!activeId || !orderId) {
            this.notification.add("Missing order line or order context. Please reload the page.", { type: "danger" });
            return false;
        }
        try {
            await applyProduct(this.props.record, result);
            console.log("✅ Order line updated successfully with:", result);
            this.notification.add("✔️ Product configured and saved to order line!", { type: "success" });
            this.pulseElement(".cpq-config-summary");
            this.pulseElement(`[data-id="${activeId}"]`);
            setTimeout(() => {
                const lineEl = document.querySelector(`[data-id="${activeId}"]`);
                if (lineEl) {
                    lineEl.scrollIntoView({ behavior: "smooth", block: "center" });
                    lineEl.classList.add("highlight-success");
                    setTimeout(() => lineEl.classList.remove("highlight-success"), 1500);
                }
            }, 300);
            if (result.sale_order_id) {
                console.log("🚀 Redirecting to Sale Order:", result.sale_order_id);
                setTimeout(() => {
                    this.env.services.action.doAction({
                        type: "ir.actions.act_window",
                        res_model: "sale.order",
                        res_id: result.sale_order_id,
                        views: [[false, "form"]],
                        target: "current",
                    });
                }, 500); // optional delay
            }
            return true;
        } catch (error) {
            console.error("❌ Failed to apply configuration result:", error);
            this.notification.add("An error occurred while updating the order line.", { type: "danger" });
            return false;
        }
    }
    
    async _showConfirmDialog(message) {
        return new Promise((resolve) => {
            console.log("📣 Opening confirmation dialog:", message);
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

    async _validate() {
        try {
            const res = await this.rpc(`/cpq/${this.props.productTmplId}/validate`, {
                combination: this.state.selected,
            });

            this.state.valid = res.valid;
            this.state.errors = res.errors;
        } catch (error) {
            console.error("❌ Validation error:", error);
            this.state.valid = false;
            this.state.errors = { general: "Validation failed." };
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

    //----------------------------------------------------------------------
    // Getters
    //----------------------------------------------------------------------

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
    const safeMany2One = (val) => Array.isArray(val) ? val[0] : val;
    const context = action.context || {};

    console.log("🚀 ConfigureDialogAction context:", context);
    console.log("🚀 active_id:", context.active_id);
    
    const productTmplId = safeMany2One(context.cpq_product_template_id);
    const orderId = safeMany2One(context.active_sale_order_id || context.sale_order_id);
    const activeId = Number(context.active_id || 0);
    const activeSaleOrderId = Number(context.active_sale_order_id || 0);
    const orderLineRecord = env.models?.["sale.order.line"]?.records?.find((rec) => rec.resId === activeId);
    const soDate = context.soDate;
    const currencyId = safeMany2One(context.currencyId);
    const companyId = safeMany2One(context.companyId);
    
    // 🧩 FIX: Ensure context contains active ids
    if (!context.active_sale_order_id && orderLineRecord?.data?.order_id?.[0]) {
        context.active_sale_order_id = orderLineRecord.data.order_id[0];
    }
    if (!context.active_id && activeId) {
        context.active_id = activeId;
    }

    if (!productTmplId || !activeId) {
        env.services.notification.add("Unable to open configurator: Missing data.", { type: "danger" });
        return;
    }

    env.services.dialog.add(ConfigureDialog, {
        title: `Configure: ${orderLineRecord.data.name || "Custom CPQ Line"}`,
        productTmplId,
        orderId,
        quantity: context.quantity || 1,
        currencyId,
        soDate,
        soDate: context.soDate,
        companyId,
        context,
        edit: true,
        cpqInitialConfig: context.cpq_initial_config || null,
        record: orderLineRecord,

        close: () => {
            console.log("🧩 Dialog close triggered. Exiting action.");
            // env.services.action.doAction({ type: "ir.actions.act_window_close" });
            env.services.action.doAction({
                type: "ir.actions.act_window",
                res_model: "sale.order",
                res_id: orderId,
                views: [[false, "form"]],
                target: "current",
            });
            // Optional improvement:
            // 👉 Uncomment to auto-reopen order form after closing configurator
            /*
            if (orderId) {
                env.services.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: "sale.order",
                    res_id: orderId,
                    views: [[false, "form"]],
                    target: "current",
                });
            }
            */
        },
        discard: () => {
            console.log("🧩 Dialog discard triggered. Exiting action.");
            // env.services.action.doAction({ type: "ir.actions.act_window_close" });
            env.services.action.doAction({
                type: "ir.actions.act_window",
                res_model: "sale.order",
                res_id: orderId,
                views: [[false, "form"]],
                target: "current",
            });
        },
        
    
    });
}


registry.category("actions").add("cpq.ConfigureDialogAction", ConfigureDialogAction);


