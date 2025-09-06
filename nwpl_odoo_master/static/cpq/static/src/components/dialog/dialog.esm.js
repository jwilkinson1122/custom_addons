/** @odoo-module **/
/* eslint-disable sort-imports */
import { scrollTo } from "@web/core/utils/scrolling";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { Component, onWillStart, useEffect, useState, useSubEnv, html } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import ProductTmplAttrib from "./product_tmpl_attrib.esm";
import SummaryPanel from "./configurator_summary_panel.esm";
import { 
    validateProps, 
    ensureStringKeys,
    nextTick, 
    useDebouncedInput, 
    debounce, 
    computeLocalCPQPriceBreakdown,
    enrichSelectedWithPreferred,
    enrichPtalIdsWithPreferences,
    mergeSelectedWithFallback,
    stripFallbackMetadata,
    flattenGroupedSelection,
    compressSharedSelections,
    normalizeSelectedStructure,
    sanitizeSelectedForBackend,
    findAttributeById,
    canonicalizeInitialSelected,
    canonicalizePrefSelected,
    canonicalizeSelectedBuckets,
    expandPtavDicts,
    getActiveTriggeredAttributeIds,
    filterVisibleAttributes,
    resolvePartnerId,
    resolveOrderId,
    resolveSaleLineId,
    tryGenerateCpqQr,
    dedupeSelected,
    isEmptySelected,
    safeParse,
    getMergedSelected,
    ensureDefaultsForRequired,
} from "./utils.esm";
import { ProductAttribGroupRenderer } from "./product_attrib_group_renderer.esm";

export class ConfigureDialog extends Component {
    static template = "cpq.ConfigureDialogDialog";
    static components = { Dialog, ProductTmplAttrib, SummaryPanel, ProductAttribGroupRenderer };

    static props = {
        orderId: Number,
        productTemplateId: Number,
        ptalIds: Array,
        initialSelected: Object,
        laterality: String,
        productTemplate: { type: Object, optional: true },
        quantity: { type: Number, optional: true },
        currencyId: { type: Number, optional: true },
        soDate: { type: String, optional: true },
        productUOMId: { type: Number, optional: true },
        pricelistId: { type: Number, optional: true },
        companyId: { type: Number, optional: true },
        cpqInitialConfig: { type: Object, optional: true },
        cpqPreferences: { type: Object, optional: true },
        partnerId: { type: Number, optional: true },
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
        
        const props = this.props;

        validateProps(this, ConfigureDialog.props);

        this.translate = {validationErrors: _t("Validation errors:"),};
        this.size = "xl";
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.dialogService = useService("dialog");
        this.actionService = useService("action");

        this.context = props.context || props.record?.model?.root?.context || {};
        this.partnerId = props.partnerId ?? resolvePartnerId(this.context, this.env);
        this.orderId = resolveOrderId(this.context, this.env);
        this.activeId = resolveSaleLineId(this.context, this.env);

        this.state = useState({
            isLoading: false,
            isInitializing: true,
            valid: false,
            lineId: this.props.activeId,
            productTemplateId: props.productTemplateId,
            productTemplate: props.productTemplate || {},
            selected: {},
            laterality: props.laterality || "bilateral",
            split: false,
            splitByAttrMap: {},
            quantityToMake: props.quantity || 1,
            errors: {},
            ptalIds: props.ptalIds || [],
            priceBreakdown: { base: 0, extras: 0, discountPct: 0, subtotal: 0, quantity: 1, total: 0 },
            undoCache: { left: null, right: null },
        });

        this.formatCurrency = (value) => {
            const number = typeof value === "number" ? value : parseFloat(value) || 0;
            return `$${number.toFixed(2)}`;
        };

        this.debouncedInput = useDebouncedInput(250);

        this.onQuantityChange = this.debouncedInput(val => {
            const parsed = parseInt(val, 10);
            this.state.quantityToMake = isNaN(parsed) || parsed < 1 ? 1 : parsed;
            this.refreshSummaryAndPricing();
        });

        this.onIncreaseQuantity = () => {
            this.state.quantityToMake += 1;
            this.refreshSummaryAndPricing();
        };

        this.onDecreaseQuantity = () => {
            if (this.state.quantityToMake > 1) {
                this.state.quantityToMake -= 1;
                this.refreshSummaryAndPricing();
            }
        };

        this.summaryKey = () => {
            try {
                return JSON.stringify(this.state.selected || {});
            } catch (e) {
                console.warn("Failed to stringify selected:", e);
                return "invalid-key";
            }
        };

        useSubEnv({
            updateQuantity: this.onQuantityChange.bind(this),
            state: this.state,
            formatCurrency: this.formatCurrency,
        });

        // this.onLateralityChange = (ev) => {
        //     this.state.laterality = ev.target.value;
        //     this.state.split = false;
        //     this.state.selected = {};
        // };

        useEffect(() => {
            this._validate();
            this.refreshSummaryAndPricing();
            console.log("[ConfigureDialog] state.selected changed:", JSON.stringify(this.state.selected, null, 2));
        }, () => [
            this.state.selected.left,
            this.state.selected.right,
            this.state.selected.shared,    
            this.state.quantityToMake,
            this.state.laterality,
            this.state.split,
        ]);


        this._refreshHandler = debounce(() => this.refreshSummaryAndPricing(), 300);

        onWillStart(this._initData.bind(this));

        console.log("[ConfigureDialog] state.selected before rendering SummaryPanel:", JSON.stringify(this.state.selected, null, 2));

    }

    // --- Data Load/Init ---------------------------------------

    async _initData() {
        // Minimal log of config sources for debugging
        const logConfig = (label, data) => {
            try { console.log(label, JSON.stringify(data, null, 2)); }
            catch (err) { console.warn(`${label} could not be stringified`, err); }
        };

        logConfig("[ConfigureDialog] props.cpqInitialConfig", this.props.cpqInitialConfig);
        logConfig("[ConfigureDialog] props.cpqPreferences", this.props.cpqPreferences);
        logConfig("[ConfigureDialog] props.context.cpq_initial_config", this.props.context?.cpq_initial_config);

        this.state.isInitializing = true;
        try {
            // --- Load template data and attribute tree
            const data = await this._loadData();
            const tmpl = data.product_tmpl_id;
            this.state.productTemplateId = tmpl.id;
            this.state.productTemplate = tmpl;
            this.title = this.props.edit
                ? _t("Edit Configuration: %s", tmpl.display_name)
                : _t("Configure: %s", tmpl.display_name);

            let attributeTree = await this.rpc(
            `/cpq/attribute/tree/${tmpl.id}`,
            { context: { partner_id: this.partnerId, user_id: this.env.services.user.userId } }
            );

            // inline normalizer (or call a shared util)
            const toObj = (v) => {
            if (v && typeof v === "object") return { ...v, id: Number(v.id ?? v[0] ?? v) };
            if (Array.isArray(v)) return { id: Number(v[0]), name: v[1] };
            return { id: Number(v) };
            };
            const normalizeNode = (n) => {
            if (!n || typeof n !== "object") return null;
            const id = Number(n.id ?? n.attribute_id ?? 0) || 0;
            const values = (n.values?.length ? n.values : (n.ptav_ids || [])).map(toObj).filter(v => Number.isFinite(v.id));
            const children = (n.children || []).map(normalizeNode).filter(Boolean);
            return { ...n, id, values, children };
            };
            attributeTree = Array.isArray(attributeTree) ? attributeTree.map(normalizeNode).filter(Boolean) : [];

            this.state.ptalIds = attributeTree;
            enrichPtalIdsWithPreferences(this.state.ptalIds, this.props.cpqPreferences?.detailed || []);

            // --- Patch UOM if needed
            if (!tmpl.uom_id) {
                const [patchedTemplate] = await this.orm.call("product.template", "read", [
                    [tmpl.id], ["name", "uom_id", "currency_id", "list_price"],
                ]);
                this.state.productTemplate = patchedTemplate;
            }

            // --- Parse config and preferences
            const rawConfig = this.props.cpqInitialConfig || this.props.context?.cpq_initial_config || {};
            const parsedConfig = safeParse(rawConfig);

            // --- Pull out split/laterality early
            // Split can also be true if any splitByAttrMap value is true (per your conventions)
            const configSplit =
                !!parsedConfig.split ||
                (parsedConfig.splitByAttrMap && Object.values(parsedConfig.splitByAttrMap).some(Boolean));
            const configLaterality = parsedConfig.laterality || this.props.laterality || "bilateral";

            // --- If selected is empty but grouped is present (edit), flatten grouped
            let effectiveSelected = parsedConfig.selected;
            if (
                (!effectiveSelected || isEmptySelected(effectiveSelected)) &&
                parsedConfig.grouped && (
                    Object.keys(parsedConfig.grouped.left || {}).length > 0 ||
                    Object.keys(parsedConfig.grouped.right || {}).length > 0 ||
                    Object.keys(parsedConfig.grouped.shared || {}).length > 0
                )
            ) {
                effectiveSelected = flattenGroupedSelection(parsedConfig.grouped);
                // Defensive: if flat, expand into shared, otherwise ensure buckets
                if (!effectiveSelected.left && !effectiveSelected.right && !effectiveSelected.shared && Object.keys(effectiveSelected).length > 0) {
                    effectiveSelected = { left: {}, right: {}, shared: effectiveSelected };
                } else {
                    effectiveSelected.left = effectiveSelected.left || {};
                    effectiveSelected.right = effectiveSelected.right || {};
                    effectiveSelected.shared = effectiveSelected.shared || {};
                }
                console.log("[CPQ Edit] Reconstructed selected from grouped:", effectiveSelected);
            }

            // --- Preferences handling
            const prefSelected = this.props.cpqPreferences?.selected || {};
            const mappedPrefs = canonicalizePrefSelected(prefSelected, this.state.ptalIds || []);


            logConfig("[ConfigureDialog] mappedPrefs", mappedPrefs);
            logConfig("[ConfigureDialog] effectiveSelected (pre-merge)", effectiveSelected);

            // Detect truly empty effectiveSelected
            const allBucketsEmpty = !effectiveSelected ||
                (Object.keys(effectiveSelected.left || {}).length === 0 &&
                Object.keys(effectiveSelected.right || {}).length === 0 &&
                Object.keys(effectiveSelected.shared || {}).length === 0);

            let mergedSelected;
            if (allBucketsEmpty) {
                mergedSelected = getMergedSelected({}, mappedPrefs, configSplit);
            } else {
                mergedSelected = getMergedSelected(effectiveSelected, mappedPrefs, configSplit);
            }


            logConfig("[ConfigureDialog] mergedSelected", mergedSelected);


            const seeded = ensureDefaultsForRequired(
                mergedSelected,
                this.state.ptalIds,
                { split: configSplit, laterality: configLaterality }
            );

            this.state.selected = canonicalizeInitialSelected({
                selected: seeded,
                split: configSplit,
                laterality: configLaterality,
            });


            this.initialPreferred = JSON.parse(JSON.stringify(this.state.selected)); 
            logConfig("[ConfigureDialog] initialPreferred", this.initialPreferred);

            this.state.split = configSplit;
            this.state.laterality = configLaterality;
            this.state.splitByAttrMap = { ...(parsedConfig.splitByAttrMap || {}) };
        
            logConfig("[ConfigureDialog] Final state.selected", this.state.selected);
           
            await nextTick();
            if (
                Object.values(this.state.selected.left || {}).length > 0 ||
                Object.values(this.state.selected.right || {}).length > 0 ||
                Object.values(this.state.selected.shared || {}).length > 0
            ) {
                await this._validate();
                this.refreshSummaryAndPricing();
            }
        } catch (error) {
            this.notification.add("Initialization failed. Please try again.", { type: "danger" });
            console.error("[ConfigureDialog] _initData error:", error);
        } finally {
            this.state.isInitializing = false;
        }
    }

    async _loadData() {
        const partnerId = resolvePartnerId(this.context, this.env);
        const orderId = resolveOrderId(this.context, this.env);
        const lineId = resolveSaleLineId(this.context, this.env);
        const productTemplateId =
            this.state.productTemplateId ||
            this.props.productTemplateId ||
            this.productTemplate?.id || null;
        if (!productTemplateId) throw new Error("Missing product template ID");
        return this.rpc(`/cpq_product_configurator/${productTemplateId}/data`, {
            context: { ...(this.context || {}), partner_id: partnerId, order_id: orderId, active_id: lineId },
        });
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
    
        console.log("Quantity updated to:", this.state.quantityToMake);
    
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

    // --- Attribute/Selection Handlers -------------------------

    async _addOrUpdateSelected(sideOrId, attributeId, valueIdOrPtavId, customValue) {
        console.log("[_addOrUpdateSelected] incoming args:", { sideOrId, attributeId, valueIdOrPtavId, customValue });

        // Defensive: must have a value id
        if (typeof valueIdOrPtavId !== "number" && typeof valueIdOrPtavId !== "string") {
            console.warn("[_addOrUpdateSelected] valueIdOrPtavId should be id (number/string), got:", valueIdOrPtavId);
            return;
        }
        const ptavId = Number(valueIdOrPtavId);
        if (!Number.isFinite(ptavId)) {
            console.warn("[_addOrUpdateSelected] Invalid ptavId:", valueIdOrPtavId, "parsed:", ptavId);
            return;
        }

        // Compute context
        const isSplit = typeof sideOrId === "string" && ["left", "right"].includes(sideOrId);
        const side = isSplit ? sideOrId : null;
        const attrId = isSplit ? attributeId : (sideOrId ?? attributeId);

        // Find attribute object
        const attr = findAttributeById(this.state.ptalIds, attrId);
        if (!attr) {
            console.warn("[_addOrUpdateSelected] Attribute not found for attrId:", attrId);
            return;
        }

        // Find PTAV
        const ptavList = Array.isArray(attr.ptav_ids) && attr.ptav_ids.length ? attr.ptav_ids : attr.values || [];
        if (!ptavList.length) {
            console.warn("[_addOrUpdateSelected] No PTAVs found for attribute:", attr);
            return;
        }
        const ptav = ptavList.find((v) => Number(v.id) === ptavId);
        if (!ptav) {
            console.warn("[_addOrUpdateSelected] PTAV not found for ptavId:", ptavId, "in", ptavList);
            return;
        }

        // Preferences (calculate preferred flags from all sources)
        let isPreferred = false, isPreferredLeft = false, isPreferredRight = false;
        const preferences = this.state.cpqPreferences;
        let pref = null;
        if (Array.isArray(preferences)) {
            pref = preferences.find(
                p => String(p.attribute_id) === String(attrId) && String(p.value_id) === String(ptavId)
            );
            if (!pref && ptav.x_virtual_cpq_id) {
                pref = preferences.find(
                    p => String(p.attribute_id) === String(attrId) && String(p.value_id) === String(ptav.x_virtual_cpq_id)
                );
            }
        }
        if (pref) {
            isPreferred = !!pref.isPreferred;
            isPreferredLeft = !!pref.isPreferredLeft;
            isPreferredRight = !!pref.isPreferredRight;
        } else if (ptav.isPreferred || ptav.isPreferredLeft || ptav.isPreferredRight) {
            isPreferred = !!ptav.isPreferred;
            isPreferredLeft = !!ptav.isPreferredLeft;
            isPreferredRight = !!ptav.isPreferredRight;
        } else if (this.initialPreferred) {
            const prefVal = this.initialPreferred.shared?.[ptavId] || this.initialPreferred.left?.[ptavId] || this.initialPreferred.right?.[ptavId];
            if (prefVal) {
                isPreferred = !!prefVal.isPreferred;
                isPreferredLeft = !!prefVal.isPreferredLeft;
                isPreferredRight = !!prefVal.isPreferredRight;
            }
        }

        // Prepare value object for selection
        let value = {
            id: ptavId,
            value: ptavId,
            note: ptav.note || "",
            linked_option_id: ptav.linked_option_id || undefined,
            isPreferred,
            isPreferredLeft,
            isPreferredRight,
        };
        if (ptav.is_custom) {
            const resolvedValue = (typeof customValue === "object" && customValue?.value !== undefined)
                ? customValue.value : customValue;
            value.value = resolvedValue;
            value.cpq_custom_type = ptav.cpq_custom_type || null;
        }
        console.log("[_addOrUpdateSelected] Final value object:", JSON.stringify(value, null, 2));

        // Always work from the full root state.selected, preserving all buckets
        let newSelected = {
            left: { ...(this.state.selected.left || {}) },
            right: { ...(this.state.selected.right || {}) },
            shared: { ...(this.state.selected.shared || {}) }
        };

        // Helper: Clear all PTAVs for this attribute in a bucket
        function clearPtavsForAttr(bucket, attr) {
            const valList = Array.isArray(attr.ptav_ids) && attr.ptav_ids.length ? attr.ptav_ids : attr.values || [];
            const allIds = new Set(valList.map(val => String(val.id)));
            for (const k of Object.keys(bucket)) {
                if (allIds.has(String(k))) {
                    delete bucket[k];
                }
            }
        }

        // Update the correct bucket, preserving others
        if (isSplit) {
            clearPtavsForAttr(newSelected[side], attr);
            newSelected[side][String(ptavId)] = value;
            console.log(`[Mode: ${side}] After update:`, JSON.stringify(newSelected[side], null, 2));
        } else if (this.state.laterality === "bilateral" && !this.state.split) {
            clearPtavsForAttr(newSelected.shared, attr);
            newSelected.shared[String(ptavId)] = value;
            console.log(`[Mode: bilateral/shared] After update:`, JSON.stringify(newSelected.shared, null, 2));
        } else if (this.state.laterality === "left") {
            clearPtavsForAttr(newSelected.left, attr);
            newSelected.left[String(ptavId)] = value;
            console.log(`[Mode: left-only] After update:`, JSON.stringify(newSelected.left, null, 2));
        } else if (this.state.laterality === "right") {
            clearPtavsForAttr(newSelected.right, attr);
            newSelected.right[String(ptavId)] = value;
            console.log(`[Mode: right-only] After update:`, JSON.stringify(newSelected.right, null, 2));
        } else {
            // fallback, treat as shared (very rare)
            clearPtavsForAttr(newSelected.shared, attr);
            newSelected.shared[String(ptavId)] = value;
            console.log(`[Mode: fallback/shared] After update:`, JSON.stringify(newSelected.shared, null, 2));
        }

        // Dedupe and ensure keys are stringified
        newSelected = dedupeSelected(newSelected, this.state.ptalIds);
        this.state.selected = ensureStringKeys(JSON.parse(JSON.stringify(newSelected)));

        // Trigger validation and UI update
        await nextTick();
        this._validate();
        this.refreshSummaryAndPricing();
    }

    _handleSharedSelect(attributeId, ev) {
        const rawValue = ev?.target?.value;
        if (!rawValue) return;
        if (typeof rawValue === "string" || typeof rawValue === "number") {
            const ptavId = parseInt(rawValue, 10);
            if (!isNaN(ptavId)) this._addOrUpdateSelected(null, attributeId, ptavId);
            return;
        }
        if (typeof rawValue === "object" && rawValue.id) {
            this._addOrUpdateSelected(null, attributeId, rawValue.id, rawValue);
        }
    }

    _handleSelect = (...args) => {
        if (args.length === 2) this._handleSharedSelect(args[0], args[1]);
        else if (args.length === 3) this._addOrUpdateSelected(args[0], args[1], args[2]);
    };

    _handleCustom = (...args) => {
        if (args.length === 4) this._addOrUpdateSelected(args[0], args[1], args[2], args[3]);
        else if (args.length === 3) this._addOrUpdateSelected(args[0], null, args[1], args[2]);
    };

    // --- UI & Mode Toggles ------------------------------------

    // Transition Behavior
    // | Transition                    | Result                                            |
    // | ----------------------------- | ------------------------------------------------- |
    // | Bilateral Shared → Left Only  | Move `shared` → `left`, clear `shared`            |
    // | Bilateral Shared → Right Only | Move `shared` → `right`, clear `shared`           |
    // | Bilateral Split → Left Only   | Retain `left`, discard `right`                    |
    // | Left Only → Bilateral Shared  | Move `left` → `shared`, clear `left`              |
    // | Bilateral Split → Shared      | Move `left` or `right` → `shared`, discard others |

    onLateralityChange = async (ev) => {
        const newLaterality = ev?.target?.value;
        const oldLaterality = this.state.laterality;

        if (!["left", "right", "bilateral"].includes(newLaterality)) {
            console.warn("[onLateralityChange] Invalid laterality:", newLaterality);
            return;
        }

        if (newLaterality === oldLaterality) return;

        console.group(`🔁 [onLateralityChange] Switching from ${oldLaterality} → ${newLaterality}`);

        const prevSelected = { ...this.state.selected };
        const shared = prevSelected.shared || {};
        const left = prevSelected.left || {};
        const right = prevSelected.right || {};
        const merged = { ...shared, ...left, ...right };

        let newSelected = {
            shared: {},
            left: {},
            right: {},
        };

        if (newLaterality === "bilateral") {
            if (this.state.split) {
                // Full split: copy everything into left/right
                for (const [ptavId, val] of Object.entries(merged)) {
                    newSelected.left[ptavId] = { ...val };
                    newSelected.right[ptavId] = { ...val };
                }
            } else {
                // Shared bilateral: put everything into shared
                newSelected.shared = { ...merged };
            }
        } else if (newLaterality === "left") {
            for (const [ptavId, val] of Object.entries(merged)) {
                newSelected.left[ptavId] = { ...val };
            }
        } else if (newLaterality === "right") {
            for (const [ptavId, val] of Object.entries(merged)) {
                newSelected.right[ptavId] = { ...val };
            }
        }

        // Clear split flags if switching to unilateral
        const goingUnilateral = newLaterality !== "bilateral";
        if (goingUnilateral) {
            this.state.split = false;
            this.state.splitByAttrMap = {};
        }

        this.state.laterality = newLaterality;
        this.state.selected = ensureStringKeys(newSelected);

        console.log("✔️ Updated laterality:", newLaterality);
        console.log("🧼 Selected:", JSON.stringify(this.state.selected, null, 2));
        console.groupEnd();

        await nextTick();
        await this._validate();
        this.refreshSummaryAndPricing();
    };

    // Global split toggle
    async onSplitToggle() {
        const wasSplit = this.state.split;
        const goingToShared = wasSplit;
        const goingToSplit = !wasSplit;

        console.group("🔀 [onSplitToggle] Toggling split mode");
        console.log("Previous split:", wasSplit);
        console.log("Going to Shared:", goingToShared, "| Going to Split:", goingToSplit);

        if (goingToShared) {
            const restoredShared = canonicalizePrefSelected(this.props.cpqPreferences?.selected || {}, this.state.ptalIds || []);
            this.state.selected = { shared: { ...restoredShared } };
            this.state.split = false;
            this.state.splitByAttrMap = {};
            console.log("[onSplitToggle] Restored to shared:", this.state.selected);
            this.refreshSummaryAndPricing();
            console.groupEnd();
            return;
        }

        if (goingToSplit) {
            const shared = { ...(this.state.selected.shared || {}) };
            const mappedPrefs = canonicalizePrefSelected(this.props.cpqPreferences?.selected || {}, this.state.ptalIds || []);
            this.state.selected.left = {};
            this.state.selected.right = {};

            // for (const attr of this.state.ptalIds || []) {
            //     for (const val of attr.values || []) {
            //         const ptavId = String(val.id);
            //         let value = shared[ptavId] || mappedPrefs[ptavId];
            //         if (!value && mappedPrefs[ptavId]) {
            //             value = mappedPrefs[ptavId];
            //         }
            //         if (value) {
            //             this.state.selected.left[ptavId] = JSON.parse(JSON.stringify(value));
            //             this.state.selected.right[ptavId] = JSON.parse(JSON.stringify(value));
            //         }
            //     }
            // }

            // const shared = { ...(this.state.selected.shared || {}) };
            for (const attr of this.state.ptalIds || []) {
                for (const val of attr.values || []) {
                    const ptavId = String(val.id);
                    let value = shared[ptavId] || mappedPrefs[ptavId];
                    if (value) {
                        this.state.selected.left[ptavId] = JSON.parse(JSON.stringify(value));
                        this.state.selected.right[ptavId] = JSON.parse(JSON.stringify(value));
                    }
                }
            }


            delete this.state.selected.shared;
            this.state.split = true;
            this.state.splitByAttrMap = {};

            for (const attr of this.state.ptalIds || []) {
                this.state.splitByAttrMap[attr.id] = true;
            }

            // Make sure keys are strings (not numbers, if any)
            this.state.selected.left = ensureStringKeys(this.state.selected.left);
            this.state.selected.right = ensureStringKeys(this.state.selected.right);

            console.log("[onSplitToggle] Converted to full split:");
            console.log("Left bucket:", this.state.selected.left);
            console.log("Right bucket:", this.state.selected.right);
            console.log("splitByAttrMap:", this.state.splitByAttrMap);
            this.refreshSummaryAndPricing();
            console.groupEnd();
        }
    }

    // Section wise split toggle
    toggleAttributeSplit(attr) {
        if (!attr || !this.state) {
            console.warn("[toggleAttributeSplit] Missing attr or state.");
            return;
        }

        const attrId = attr.id;
        const ptavIds = (attr.values || []).map(v => String(v.id));
        const isCurrentlySplit = !!this.state.splitByAttrMap?.[attrId];
        const mappedPrefs = canonicalizePrefSelected(this.props.cpqPreferences?.selected || {}, this.state.ptalIds || []);
        const newSplitByAttrMap = { ...this.state.splitByAttrMap, [attrId]: !isCurrentlySplit };

        this.state.selected.left = this.state.selected.left || {};
        this.state.selected.right = this.state.selected.right || {};
        this.state.selected.shared = this.state.selected.shared || {};

        console.group(`🔀 [toggleAttributeSplit] Attribute ID: ${attrId} | Current: ${isCurrentlySplit} -> ${!isCurrentlySplit}`);

        if (!isCurrentlySplit) {
            // Move from shared → left/right
            // for (const ptavId of ptavIds) {
            //     let val = this.state.selected.shared[ptavId] || mappedPrefs[ptavId];
            //     if (val) {
            //         this.state.selected.left[ptavId] = { ...val };
            //         this.state.selected.right[ptavId] = { ...val };
            //         delete this.state.selected.shared[ptavId];
            //     }
            // }
            for (const ptavId of ptavIds) {
                let val = this.state.selected.shared[ptavId] || mappedPrefs[ptavId];
                if (!val && mappedPrefs[ptavId]) val = mappedPrefs[ptavId];
                if (val) {
                    this.state.selected.left[ptavId] = JSON.parse(JSON.stringify(val));
                    this.state.selected.right[ptavId] = JSON.parse(JSON.stringify(val));
                    delete this.state.selected.shared[ptavId];
                }
            }
        } else {
            // Move from left/right → shared
            for (const ptavId of ptavIds) {
                let val = this.state.selected.left[ptavId] || this.state.selected.right[ptavId] || mappedPrefs[ptavId];
                if (val) this.state.selected.shared[ptavId] = { ...val };
                delete this.state.selected.left[ptavId];
                delete this.state.selected.right[ptavId];
            }
        }

        this.state.splitByAttrMap = newSplitByAttrMap;
        this.state.split = Object.values(newSplitByAttrMap).some(Boolean);

        console.log("Updated splitByAttrMap:", this.state.splitByAttrMap);
        console.log("Left bucket:", this.state.selected.left);
        console.log("Right bucket:", this.state.selected.right);
        console.log("Shared bucket:", this.state.selected.shared);

        this.refreshSummaryAndPricing();
        console.groupEnd();
    }

    isAttributeSplit(attrId) {
        return !!this.state.splitByAttrMap[attrId];
    }

    async _validate() {
        const productTemplateId = this.productTemplateId;
        if (!productTemplateId) return;
        const sel = this.state.selected || {};

        const isSplit = this.state.split || Object.values(this.state.splitByAttrMap).some(Boolean);
        
        if (isEmptySelected(this.state.selected)) {
            const seeded = ensureDefaultsForRequired(
                this.state.selected,
                this.state.ptalIds,
                { split: isSplit, laterality: this.state.laterality }
            );
            this.state.selected = ensureStringKeys(seeded);
        }
        // Always use bucketed structure for CPQ backend
        const combination = {
            selected: canonicalizeSelectedBuckets(sel, isSplit, this.state.laterality)
        };
        const hasSelection = ["left", "right", "shared"].some(
            k => combination.selected[k] && Object.keys(combination.selected[k]).length > 0
        );
        if (!hasSelection) {
            this.state.valid = false;
            this.state.errors = {};
            return;
        }
        try {
            console.log("[_validate] Sending combination.selected to backend:", JSON.stringify(combination.selected, null, 2));
            const res = await this.rpc(
                `/cpq/${productTemplateId}/validate`,
                { combination, context: { ...this.context, skip_cpq_validate_ptav_ids: true } }
            );
            this.state.valid = !!res.valid;
            this.state.errors = res.errors || {};
        } catch (e) {
            this.state.valid = false;
            this.state.errors = { general: "Validation RPC error." };
        }
    }

    canCreate() {
        return this.state.valid;
    }

    onCreate = debounce(async () => {
        if (this.state.isLoading) return;
        const { orderId, activeId } = this._resolveOrderAndLineContext();
        if (!orderId || !activeId || !this.productTemplateId) {
            this.notification.add("Missing order, line, or template ID. Cannot continue.", { type: "danger" });
            return;
        }

        let productTemplate = this.productTemplate;
        if (!productTemplate?.uom_id) {
            const [tpl] = await this.orm.call("product.template", "read", [[this.productTemplateId], ["uom_id"]]);
            productTemplate = tpl;
        }

        if (!(await this._showConfirmDialog("Save this configuration to the order?"))) return;

        this.state.isLoading = true;
        await this.env.services.ui.block();

        await this._validate();
        if (!this.state.valid) {
            this.notification.add("Please fix the validation errors before saving.", { type: "warning" });
            await this.env.services.ui.unblock();
            this.state.isLoading = false;
            return;
        }

        await nextTick();
        this.refreshSummaryAndPricing();

        let enrichedSelected = enrichSelectedWithPreferred(this.state.selected, this.state.ptalIds);

        let hasAnySelected =
            (enrichedSelected.left && Object.keys(enrichedSelected.left).length > 0) ||
            (enrichedSelected.right && Object.keys(enrichedSelected.right).length > 0) ||
            (enrichedSelected.shared && Object.keys(enrichedSelected.shared).length > 0);

        if (!hasAnySelected) {
            const prefs = this.props.cpqPreferences?.selected || {};
            const defaultBuckets = this.state.split ? ["left", "right"] : ["shared"];
            for (const ptavId of Object.keys(prefs)) {
                for (const bucket of defaultBuckets) {
                    enrichedSelected[bucket] = enrichedSelected[bucket] || {};
                    enrichedSelected[bucket][ptavId] = {
                        id: ptavId,
                        value: ptavId,
                        isPreferred: true,
                    };
                }
            }
        }

        const isSplit = this.state.split || Object.values(this.state.splitByAttrMap).some(Boolean);

        let config = {
            selected: canonicalizeSelectedBuckets(
                enrichedSelected,
                isSplit,
                this.state.laterality
            ),
            split: this.state.split,
            laterality: this.state.laterality,
        };

        config = normalizeSelectedStructure(config);

        config.grouped = {
            left: config.selected.left || {},
            right: config.selected.right || {},
            shared: config.selected.shared || {},
        };

        let stillNoSelection =
            (!config.selected.left || Object.keys(config.selected.left).length === 0) &&
            (!config.selected.right || Object.keys(config.selected.right).length === 0) &&
            (!config.selected.shared || Object.keys(config.selected.shared).length === 0);

        if (stillNoSelection && config.grouped && Object.keys(config.grouped.shared || {}).length > 0) {
            config.selected = {
                left: config.grouped.left || {},
                right: config.grouped.right || {},
                shared: config.grouped.shared || {},
            };
            config = normalizeSelectedStructure({
                selected: config.selected,
                split: config.split,
                laterality: config.laterality,
            });
        }

        if (
            config.split === true &&
            config.laterality === "bilateral" &&
            config.selected &&
            Object.keys(config.selected.shared || {}).length > 0 &&
            Object.keys(config.selected.left || {}).length === 0 &&
            Object.keys(config.selected.right || {}).length === 0
        ) {
            config.selected.left = { ...config.selected.shared };
            config.selected.right = { ...config.selected.shared };
            config.selected.shared = {};
        }

        const summary = this.summaryApi?.getSummaryState?.() || {};
        const productUom = Array.isArray(productTemplate.uom_id) ? productTemplate.uom_id[0] : productTemplate.uom_id;

        config.ptal_ids = this.state.ptalIds || [];
        Object.assign(config, {
            splitByAttrMap: this.state.splitByAttrMap,
            name: this.productTemplateName,
            laterality: this.state.laterality,
            split: isSplit,
            quantity_to_make: this.state.quantityToMake,
            product_uom_qty: this.state.quantityToMake,
            product_uom: productUom,
            price_unit: this.state.quantityToMake > 0
                ? parseFloat((this.state.priceBreakdown.total / this.state.quantityToMake).toFixed(2))
                : 0,
            left_price: summary.left || 0,
            right_price: summary.right || 0,
            total_price: summary.total || 0,
            cpqPreferences: this.state.preferences || [],
            product_template_id: this.productTemplateId,
        });

        console.group("[CPQ onCreate] FINAL config to backend");
        console.log("config.splitByAttrMap:", config.splitByAttrMap);
        console.log("config.selected:", JSON.stringify(config.selected, null, 2));
        console.log("config.grouped:", JSON.stringify(config.grouped, null, 2));
        console.groupEnd();

        try {
            const summary_html = await this.rpc("/cpq/config/summary", { config_data: config });
            config.configuration_summary = summary_html;
        } catch (err) {
            config.configuration_summary = "";
            console.warn("Could not fetch summary_html before save.", err);
        }

        const contextPayload = {
            active_model: "sale.order.line",
            active_id: this.props.activeId || this.context?.active_id,
            active_sale_order_id: this.props.orderId || this.context?.active_sale_order_id,
            partner_id: this.props.partnerId || this.context?.partner_id,
            ...(this.context || {}),
        };

        try {
            console.group("[CPQ onCreate] SENDING TO BACKEND");
            console.log("config:", JSON.stringify(config, null, 2));
            console.groupEnd();

            console.log("Sending config.selected to backend:", JSON.stringify(config.selected, null, 2));

            const response = await this.rpc(
                `/cpq_product_configurator/${this.productTemplateId}/configure`,
                { configuration: config, context: { ...contextPayload, partner_id: this.partnerId } }
            );

            if (response?.configuration) {
                this.notification.add("Configuration successfully saved to order line.", { type: "success" });
                await this.props.record?.load?.();
                this.pulseElement(".cpq-config-summary");
                const qrTarget = document.querySelector("#cpq-canonical-qr");
                if (qrTarget) await tryGenerateCpqQr(this.rpc, activeId, qrTarget);
                this._redirectToOrder(orderId);
            } else {
                this.notification.add("Unexpected server response. Please try again.", { type: "danger" });
            }
        } catch (error) {
            this.notification.add("An error occurred while saving configuration.", { type: "danger" });
            console.error("Failed to save configuration:", error);
        } finally {
            this.state.isLoading = false;
            await this.env.services.ui.unblock();
        }
    });

    refreshSummaryAndPricing() {
        console.log("[refreshSummaryAndPricing] selected =", JSON.stringify(this.state.selected, null, 2));

         const config = {
            selected: this.state.selected,
            laterality: this.state.laterality,
            split: this.state.split,
            ptalIds: this.state.ptalIds,
            splitByAttrMap: this.state.splitByAttrMap,
            productTemplate: this.productTemplate,
            quantityToMake: this.state.quantityToMake,
        };
        
        // const config = {
        //     selected: this.state.selected,
        //     laterality: this.state.laterality,
        //     ptal_ids: this.state.ptalIds,
        //     splitByAttrMap: this.state.splitByAttrMap,
        // };

        if (this.summaryApi?.computeSummary) {
            this.summaryApi.computeSummary(config); 
        }

        this.updatePricePreview();
    }

    async updatePricePreview() {
        const productTemplateId = this.productTemplateId;
        if (!productTemplateId) return;
        const isSplit = this.state.split || Object.values(this.state.splitByAttrMap).some(Boolean);
        const combination = {
            selected: canonicalizeSelectedBuckets(this.state.selected, isSplit, this.state.laterality)
        };
        const contextPayload = {
            active_model: "sale.order.line",
            active_id: this.props.context?.active_id || this.props.record?.resId,
            order_id: this.props.orderId,
            active_sale_order_id: this.props.orderId,
            partner_id: this.partnerId,
            ...(this.props.context || {}),
        };
        try {
            const response = await this.rpc(
                `/cpq/${productTemplateId}/price_preview`,
                { configuration: combination, context: { ...contextPayload } }
            );
            if (response?.breakdown) {
                this.state.priceBreakdown = response.breakdown;
                return;
            }
        } catch (err) {}
        // Fallback local estimate
        const base = this.productTemplate?.list_price || 0;
        const extras = this.summaryApi?.getSummaryState?.().priceSummary.extrasSubtotal || 0;
        const quantity = this.state.quantityToMake || 1;
        this.state.priceBreakdown = computeLocalCPQPriceBreakdown({ basePrice: base, extras, quantity });
    }

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
        let activeId =
            props.activeId ||
            context.active_id ||
            (props.record?.resId && typeof props.record.resId === "number" ? props.record.resId : null);
        const isVirtual = !activeId || (typeof activeId === "string" && activeId.startsWith("virtual_"));
        if (this.props.edit && (!activeId || isVirtual)) {
            this.notification.add("This configuration must be saved before editing.", { type: "danger" });
            throw new Error("Missing order line ID in edit mode.");
        }
        return { orderId, activeId, isVirtual };
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

    pulseElement(selector) {
        const element = document.querySelector(selector);
        if (!element) return;
        element.classList.remove("highlight-success");
        void element.offsetWidth;
        element.classList.add("highlight-success");
    }

    async _redirectToOrder(orderId) {
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "sale.order",
            res_id: orderId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    _cleanSide(side) {
        if (this.state.selected?.[side]) {
            delete this.state.selected[side];
        }
    }

    // copyLeftToRight

    // copyRightToLeft

    _restoreUndoCache() {
        if (this.state.undoCache.left) {
            this.state.selected.left = ensureStringKeys(JSON.parse(JSON.stringify(this.state.undoCache.left)));

        }
        if (this.state.undoCache.right) {
            this.state.selected.right = ensureStringKeys(JSON.parse(JSON.stringify(this.state.undoCache.right)));

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

    async onClose() {
        await this._closeDialog();
    }

    async _closeDialog(force = false) {
        if (!force && this._hasUnsavedChanges?.()) {
            const confirmed = await this._showConfirmDialog("You have unsaved configuration changes. Exit anyway?");
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
            console.log("Resetting selections only (keeping quantity and laterality).");
        
            this.state.selected = ensureStringKeys(JSON.parse(JSON.stringify(this.initialState.selected)));

            await nextTick();
        
            await this._validate();
            this.summaryApi?.computeSummary?.();
            this.updatePricePreview();

            this.notification.add("Attribute selections reset.", { type: "success" });
        } catch (error) {
            console.error("Failed to reset selections:", error);
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
            console.log("Resetting to initial state:", this.initialState);
        
            this.state.laterality = this.initialState.laterality;
            this.state.split = this.initialState.split;
            this.state.quantityToMake = this.initialState.quantityToMake;
            this.state.selected = ensureStringKeys(JSON.parse(JSON.stringify(this.initialState.selected)));

            await nextTick();
            await this._validate();
            this.summaryApi?.computeSummary?.();
            this.updatePricePreview();

            this.notification.add("Configuration reset to defaults.", { type: "success" });
            this.pulseElement(".cpq-config-summary");
            this.pulseElement(".pricing-summary"); // Optional: if you want price totals to animate
            this.summaryApi?.showToast?.("Configuration reset!");
        } catch (error) {
            console.error("Failed to reset configuration:", error);
            this.notification.add("An error occurred while resetting.", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
        
    }

    //---------------------------------------------------------------------
    // Getters and Setters
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

    get allAttributes() {
        return this.state.ptalIds;
    }

    get visibleAttributes() {
        const selected = this.state.selected || {};
        const all = this.state.ptalIds || [];
    
        const hasAnySelection = Object.values(selected).some(val => {
            return typeof val === "object"
                ? Object.keys(val).length > 0
                : !!val;
        });
    
        if (!hasAnySelection) {
            console.warn("No selection yet — evaluating visibility based on trigger rules");
        }
        
        const triggerMap = getActiveTriggeredAttributeIds(selected, all);
        const visible = filterVisibleAttributes(all, triggerMap);
    
        // Debug flattened visible attribute IDs
        const allVisibleIds = new Set();
        function collectVisibleIds(attrs) {
            for (const a of attrs) {
                allVisibleIds.add(a.id);
                if (a.children?.length) {
                    collectVisibleIds(a.children);
                }
            }
        }
        collectVisibleIds(visible);
    
        // Debug what's visible vs. total
        const allAttrIds = new Set();
        function collectAllIds(attrs) {
            for (const a of attrs) {
                allAttrIds.add(a.id);
                if (a.children?.length) {
                    collectAllIds(a.children);
                }
            }
        }
        collectAllIds(all);
    
        const hiddenIds = [...allAttrIds].filter(id => !allVisibleIds.has(id));
        console.groupCollapsed("Custom Visibility Debug");
        console.log("Visible Attribute IDs:", [...allVisibleIds]);
        console.log("Hidden Attribute IDs:", hiddenIds);
        console.groupEnd();
    
        return visible;
    }

    get finalCombinationForBackend() {
        const compressed = compressSharedSelections(
            this.state.selected,
            this.state.laterality,
            this.state.split
        );

        const result = {};

        // Accept both old isPreferred and new isPreferredLeft/Right for flexibility
        const processDict = (dict, side = null) => {
            const processed = {};
            for (const [ptavId, value] of Object.entries(dict || {})) {
                const id = parseInt(ptavId, 10);
                if (!id || isNaN(id)) continue;

                let preferredProps = {};
                if (side === "left") {
                    preferredProps.isPreferredLeft = value.isPreferredLeft ?? value.isPreferred ?? false;
                } else if (side === "right") {
                    preferredProps.isPreferredRight = value.isPreferredRight ?? value.isPreferred ?? false;
                } else {
                    // Shared or unknown: pass both, fallback to single if present
                    preferredProps.isPreferredLeft = value.isPreferredLeft ?? value.isPreferred ?? false;
                    preferredProps.isPreferredRight = value.isPreferredRight ?? value.isPreferred ?? false;
                }

                processed[id] = typeof value === "object" && "value" in value
                    ? {
                        id,
                        value: value.value,
                        cpq_custom_type: value.cpq_custom_type || null,
                        ...preferredProps,
                        note: value.note || "",
                        linked_option_id: value.linked_option_id || undefined,
                    }
                    : {
                        id,
                        value: id,
                        ...preferredProps,
                        note: "",
                        linked_option_id: undefined,
                    };
            }
            return processed;
        };

        const hasLeft = compressed?.left && Object.keys(compressed.left).length > 0;
        const hasRight = compressed?.right && Object.keys(compressed.right).length > 0;
        const hasShared = !compressed.left && !compressed.right;

        if (hasLeft || hasRight) {
            if (hasLeft) result.left = processDict(compressed.left, "left");
            if (hasRight) result.right = processDict(compressed.right, "right");
        }

        if (hasShared) {
            result.selected = processDict(compressed);
        }

        console.log("Final flattened combination sent to backend:", JSON.stringify(result, null, 2));
        return expandPtavDicts(result);
    }

    get groupedCombinationForBackend() {
        // Just use current selected, not "enriched"
        const compressed = compressSharedSelections(
            this.state.selected,
            this.state.laterality,
            this.state.split
        );

        const processDict = (dict, side = null) => {
            const result = {};
            for (const [ptavId, value] of Object.entries(dict || {})) {
                const id = parseInt(ptavId, 10);
                if (!id || isNaN(id)) continue;

                let preferredProps = {};
                if (side === "left") {
                    preferredProps.isPreferredLeft = value.isPreferredLeft ?? value.isPreferred ?? false;
                } else if (side === "right") {
                    preferredProps.isPreferredRight = value.isPreferredRight ?? value.isPreferred ?? false;
                } else {
                    preferredProps.isPreferredLeft = value.isPreferredLeft ?? value.isPreferred ?? false;
                    preferredProps.isPreferredRight = value.isPreferredRight ?? value.isPreferred ?? false;
                }

                result[id] = typeof value === "object" && "value" in value
                    ? {
                        id,
                        value: value.value,
                        cpq_custom_type: value.cpq_custom_type || null,
                        ...preferredProps,
                        note: value.note || "",
                        linked_option_id: value.linked_option_id || undefined,
                    }
                    : {
                        id,
                        value: id,
                        ...preferredProps,
                        note: "",
                        linked_option_id: undefined,
                    };
            }
            return result;
        };

        const grouped = {};
        const hasLeft = compressed?.left && Object.keys(compressed.left).length > 0;
        const hasRight = compressed?.right && Object.keys(compressed.right).length > 0;

        if (hasLeft || hasRight) {
            if (hasLeft) grouped.left = processDict(compressed.left, "left");
            if (hasRight) grouped.right = processDict(compressed.right, "right");
        } else {
            grouped.selected = processDict(compressed);
        }

        return expandPtavDicts(grouped);
    }

    get enrichedConfigForBackend() {
        const compressed = compressSharedSelections(
            this.state.selected, 
            this.state.laterality, 
            this.state.split
        );
        const stripped = stripFallbackMetadata(compressed);
        const enriched = enrichSelectedWithPreferred(stripped, this.state.ptalIds || []);

        if (!enriched || typeof enriched !== "object") {
            return {};
        }

        // 🔒 Helper to safely filter a flat dict of ptavId → value
        const filterValidEntries = (obj = {}) =>
            Object.fromEntries(
                Object.entries(obj).filter(
                    ([, val]) => val && typeof val === "object" && !Array.isArray(val)
                )
            );

        // 🧠 Handle both flat and split formats
        if (enriched.left || enriched.right) {
            return {
                left: filterValidEntries(enriched.left),
                right: filterValidEntries(enriched.right),
            };
        }

        return filterValidEntries(enriched);
    }

}

export function ConfigureDialogAction(env, action) {
    const context = action.context || {};
    console.log("[ConfigureDialogAction] cpqInitialConfig:", JSON.stringify(
        context.cpq_initial_config || context.cpq_configuration_json || context.configuration || null,
        null, 2
    ));
    const rawTmpl = context.product_tmpl_id || context.product_template_id || context.cpq_product_template_id;
    const productTemplate = typeof rawTmpl === "object" ? rawTmpl : undefined;
    const productTemplateId = typeof rawTmpl === "object" ? rawTmpl.id : rawTmpl;
    const orderLineData = env.services.model?.root?.data?.order_line;
    const orderId = resolveOrderId(context, env);
    const activeId = resolveSaleLineId(context, env);
    const resolvedPartnerId = resolvePartnerId(context, env);
    const partnerId = Number.isNaN(Number(resolvedPartnerId)) ? null : Number(resolvedPartnerId);
    const currencyId = context.currencyId || context.currency_id;
    const soDate = context.soDate || context.so_date || new Date().toISOString().split("T")[0];
    const quantity = typeof context.quantity === "number" ? context.quantity : 1;
    const cpqInitialConfig = safeParse(context.cpq_initial_config || context.cpq_configuration_json || context.configuration || null);

    const ptalIds = context.ptal_ids || [];  // Or fetch these elsewhere as needed
    const initialSelected = context.initial_selected || {};
    const laterality = context.laterality || "bilateral";

    const isVirtual = typeof activeId === "string" && activeId.startsWith("virtual_");
    const isEdit = context.edit === true && typeof activeId === "number" && activeId > 0;

    if (isEdit && (!activeId || isVirtual)) {
        env.services.notification.add(_t("This configuration must be saved before editing."), { type: "warning" });
        return;
    }

    const missingProps = [];
    if (!productTemplateId) missingProps.push("productTemplateId");
    if (!orderId) missingProps.push("orderId");
    if (!currencyId) missingProps.push("currencyId");
    if (!soDate) missingProps.push("soDate");
    if (missingProps.length) {
        env.services.notification.add(_t("Cannot open configurator. Missing: ") + missingProps.join(", "), { type: "danger" });
        return;
    }

    const fullContext = { ...context, active_model: "sale.order.line", active_id: activeId, active_sale_order_id: orderId, partnerId };
    if (activeId && orderLineData?.records) {
        orderLineData.records = orderLineData.records.filter(line => line.resId === activeId);
        orderLineData.leaveEditMode?.();
    }

    env.services.dialog.add(ConfigureDialog, {
        productTemplateId: Number(productTemplateId),
        productTemplate: productTemplate || {},
        orderId: Number(orderId),
        currencyId: Number(currencyId),
        soDate: String(soDate),
        quantity: Number(quantity),
        context: fullContext || {},
        edit: !!isEdit,
        partnerId: partnerId ? Number(partnerId) : undefined,
        activeId: (typeof activeId === "number" || typeof activeId === "string") ? activeId : undefined,
        // activeId: { type: [Number, String], optional: true },
        // lineId: typeof activeId === "number" || typeof activeId === "string" ? activeId : undefined,
        cpqInitialConfig,
        ptalIds,
        initialSelected,
        laterality,
        // save: null, 
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
    });
}

registry.category("actions").add("cpq.ConfigureDialogAction", ConfigureDialogAction);
