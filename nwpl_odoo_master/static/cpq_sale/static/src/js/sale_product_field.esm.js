/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { useService } from "@web/core/utils/hooks";
import { ConfigureDialog } from "@nwpl_odoo_master/static/cpq/components/dialog/dialog.esm";
import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from "@web/core/network/rpc_service";
import { safeMany2One, mergeSelectedWithFallback, flattenGroupedSelection,isEmptySelected, } from "@nwpl_odoo_master/static/cpq/components/dialog/utils.esm";

patch(SaleOrderLineProductField.prototype, {
    setup() {
        super.setup(...arguments);
        this.dialogService = useService("dialog");
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.skipNextProductTemplateUpdate = false;
    },

    _isBackendCpq(result) {
        return result?.mode === "configurator";
    },
    _isFrontendCpq() {
        return !!this.props.record.data.product_template_id_cpq_ok;
    },
    _isCpq(result) {
        return this._isBackendCpq(result) || this._isFrontendCpq();
    },

    async _onProductTemplateUpdate() {
        if (this.skipNextProductTemplateUpdate) {
            this.skipNextProductTemplateUpdate = false;
            return;
        }
        const templateId = this.props.record.data.product_template_id?.[0];
        if (!templateId) return;
        const result = await this.orm.call(
            "product.template", "get_single_product_variant", [templateId], { context: this.context }
        );
        if (this._isCpq(result)) {
            return this._cpqConfigureDialog(result);
        }
        if (result && result.product_id) {
            await this.props.record.update({
                product_id: Array.isArray(result.product_id)
                    ? result.product_id
                    : [result.product_id, result.product_name],
                product_uom: safeMany2One(result.uom_id),
                price_unit: result.price_unit,
            });
            await this._onProductUpdate();
        } else {
            this.notification.add(_t("No variant found or invalid Custom mode."), { type: "danger" });
        }
    },

    async _onProductUpdate() {
        if (this._isFrontendCpq()) return;
        const productId = Array.isArray(this.props.record.data.product_id)
            ? this.props.record.data.product_id[0]
            : this.props.record.data.product_id;
        if (productId) {
            const [product] = await this.orm.call("product.product", "read", [[productId], ["uom_id", "lst_price", "name"]]);
            await this.props.record.update({
                product_uom: safeMany2One(product.uom_id),
                product_id: [productId, product.name],
                price_unit: product.lst_price,
                name: product.name,
            });
        }
    },

    onProductChange(ev) {
        if (this._isFrontendCpq()) return;
        return super.onProductChange(...arguments);
    },

    _editProductConfiguration() {
        if (this._isFrontendCpq()) {
            console.log("Custom Product detected — opening configurator.");
            return this._cpqConfigureDialog();
        }
        console.log("🛑 Non-Custom product — using native Odoo flow.");
        return super._editProductConfiguration(...arguments);
    },

    async _openProductConfigurator(edit = false) {
        if (!this._isFrontendCpq()) {
            return super._openProductConfigurator(...arguments);
        }
        return this._cpqConfigureDialog();
    },

    async _cpqConfigureDialog(result = null) {
        if (result && !this._isCpq(result)) return;
        this.skipNextProductTemplateUpdate = false;

        const safeRead = async (model, ids, fieldList) => {
            const idList = Array.isArray(ids) ? ids : [ids];
            const result = await this.orm.call(model, "read", [idList, fieldList]);
            const record = Array.isArray(result) ? result[0] : result;
            ["product_uom", "product_id", "order_id", "product_template_id", "currency_id", "company_id"].forEach((field) => {
                if (record[field]) record[field] = safeMany2One(record[field]);
            });
            return record;
        };

        // const updateRoot = async (backendData) => {
        //     const root = this.props.record.model.root;
        //     if (!root) return;
        //     const rootFields = Object.keys(root.data || {});
        //     const safeData = {};
        //     for (const [k, v] of Object.entries(backendData || {})) {
        //         if (rootFields.includes(k)) safeData[k] = v;
        //     }
        //     if (backendData.id && !root.resId) safeData.id = backendData.id;
        //     if (Object.keys(safeData).length) await root.update(safeData);
        // };

        const updateRoot = async (backendData) => {
            const root = this.props.record.model.root;
            if (!root) return;

            const rootFields = Object.keys(root.data || {});
            const safeData = {};

            for (const [k, v] of Object.entries(backendData || {})) {
                if (!rootFields.includes(k)) continue;

                // ⛔️ Do not change company_id once the root has one
                if (k === "company_id") {
                    const cur = root.data.company_id?.[0] || null;
                    const incoming = Array.isArray(v) ? v[0] : (typeof v === "number" ? v : null);
                    if (cur) continue;                 // already set → skip
                    if (cur === incoming) continue;    // equal → skip
                }

                safeData[k] = v;
            }

            if (backendData.id && !root.resId) safeData.id = backendData.id;
            if (Object.keys(safeData).length) await root.update(safeData);
        };


        // ---- Resolve current context -----------------------------------------
        let activeId = this.props.record.resId || null;
        let orderId =
            this.props.record.data.order_id?.[0] ||
            this.props.record.model.root?.resId ||
            null;

        const productTemplateId = safeMany2One(this.props.record.data.product_template_id)[0];

        // let partnerIdRaw =
        //     this.props.record.data.partner_id?.[0] ||
        //     this.props.record.data.order_partner_id?.[0] ||
        //     null;

        const root = this.props.record.model.root;
        let partnerIdRaw =
            this.props.record.data.partner_id?.[0] ||
            this.props.record.data.order_partner_id?.[0] ||
            root?.data?.partner_id?.[0] ||                    // <— read partner from the unsaved sale.order form
            root?.data?.order_partner_id?.[0] ||              // <— extra safety if you mirror it there
            null;

        if (!partnerIdRaw && orderId) {
            try {
                const [order] = await this.orm.call("sale.order", "read", [[orderId], ["partner_id"]]);
                partnerIdRaw = order?.partner_id?.[0] || null;
            } catch (_) {}
        }
        const partnerId = Number.isInteger(partnerIdRaw) && partnerIdRaw > 0 ? partnerIdRaw : null;
        let isVirtual = activeId && typeof activeId === "string" && activeId.startsWith("virtual");

        // ---- Helper: create an order if needed -------------------------------
        const ensureOrderId = async () => {
            if (orderId) return orderId;
            if (!partnerId) {
                this.notification.add(_t("Select a customer before configuring the product."), { type: "warning" });
                return null;
            }
            const companyId =
                this.props.record.data.company_id?.[0] ||
                this.props.record.model.root?.data?.company_id?.[0] ||
                this.env.company.id;

            // Try to reuse partner’s pricelist; let server compute the rest.
            let pricelistId = null;
            try {
                const [p] = await this.orm.call("res.partner", "read", [[partnerId], ["property_product_pricelist"]]);
                pricelistId = p?.property_product_pricelist?.[0] || null;
            } catch (_) {}

            const newOrderId = await this.orm.call("sale.order", "create", [{
                partner_id: partnerId,
                company_id: companyId,
                ...(pricelistId ? { pricelist_id: pricelistId } : {}),
            }]);

            // Reflect the new order in the UI root record (so no longer virtual)
            const orderData = await safeRead("sale.order", newOrderId, ["id", "name", "partner_id", "pricelist_id", "currency_id"]);
            await updateRoot(orderData);

            orderId = newOrderId;
            return orderId;
        };

        // ---- We only truly require a product template; we can create an order now
        if (!productTemplateId) {
            this.notification.add(_t("Cannot open configurator: missing product template."), { type: "danger" });
            return;
        }
        orderId = await ensureOrderId();
        if (!orderId) return;

        const safeFrontendUpdate = async (record, backendData) => {
            const frontendFields = Object.keys(record.data || {});
            const safeData = {};
            for (const [key, value] of Object.entries(backendData || {})) {
                if (frontendFields.includes(key)) safeData[key] = value;
            }
            if (backendData.id && !record.resId) safeData.id = backendData.id;
            if (Object.keys(safeData).length > 0) await record.update(safeData);
        };

        // ---- Proceed as before (with optional cleanup flags) ------------------
        let createdOrderId = null;
        let createdLineId = null;

        this.notification.add(_t("Preparing your configuration..."), { type: "info" });
        try {
            // Create a new line if needed
            if (!activeId || isVirtual) {
                const { product_id } = await this.orm.call("product.template", "ensure_configurator_product", [productTemplateId]);
                const { uom_id } = await safeRead("product.template", productTemplateId, ["uom_id"]);
                const createdId = await this.orm.call("sale.order.line", "create", [{
                    order_id: orderId,
                    product_template_id: productTemplateId,
                    product_id: product_id,
                    product_uom: uom_id[0],
                    product_uom_qty: 1,
                    name: "Custom Line",
                    price_unit: 0.0,
                }]);
                activeId = Array.isArray(createdId) ? createdId[0] : createdId;
                createdLineId = activeId;

                const lineData = await safeRead("sale.order.line", activeId, [
                    "order_id", "product_template_id", "product_uom_qty", "currency_id", "company_id", "name", "product_uom", "product_id"
                ]);
                await safeFrontendUpdate(this.props.record, lineData);
                this.notification.add(_t("Order line created! Opening configurator..."), { type: "success" });
                this._pulseLine(activeId);
                isVirtual = false;
            }

            const isEdit = activeId && typeof activeId === "number" && !isVirtual;

            // Preferences
            let preferences = {};
            if (partnerId && productTemplateId) {
                try {
                    preferences = await jsonrpc("/cpq/preferences/resolve", {
                        partner_id: partnerId,
                        product_template_id: productTemplateId,
                    });
                } catch (_) {}
            }

            // Base config
            const rawConfig = this.props.record.data.cpq_configuration_json;
            let baseConfig = {};
            try {
                baseConfig = typeof rawConfig === "string" ? JSON.parse(rawConfig) : (rawConfig || {});
            } catch (_) {}

            let selected = baseConfig.selected;
            if (isEmptySelected(selected)) {
                if (baseConfig.grouped && Object.keys(baseConfig.grouped).length) {
                    const flat = flattenGroupedSelection(baseConfig.grouped || {});
                    selected = mergeSelectedWithFallback(flat, {});
                    console.warn("🩹 Reconstructed selected from grouped for edit:", selected);
                } else {
                    selected = { left: {}, right: {}, shared: {} };
                }
            }
            if (!isEdit && preferences.selected) {
                selected = mergeSelectedWithFallback(selected || {}, preferences.selected || {});
            }

            // Pull PTALs
            const ptalData = await jsonrpc(`/cpq_product_configurator/${productTemplateId}/data`, {});
            const laterality = baseConfig.laterality ?? preferences.laterality ?? "bilateral";

            // Mark whether we created the order in this flow (for cleanup)
            // (We can detect by comparing root.resId before/after; here we just set it if it didn't exist at entry.)
            createdOrderId = this.props.record.model.root?._previousResId ? null : orderId;

            // Open dialog
            this.dialogService.add(ConfigureDialog, {
                ptalIds: ptalData?.ptal_ids || [],
                record: this.props.record,
                orderId,
                activeId,
                partnerId,
                productTemplateId,
                edit: isEdit,
                cpqInitialConfig: baseConfig,
                initialSelected: selected,
                laterality,
                cpqPreferences: preferences,
                close: () => this.notification.add(_t("Configurator closed."), { type: "info" }),
                discard: async () => {
                    // Optional cleanup of created line/order if user discards
                    try {
                        if (createdLineId) {
                            await this.orm.call("sale.order.line", "unlink", [[createdLineId]]);
                        }
                        if (createdOrderId) {
                            const linesCount = await this.orm.call("sale.order.line", "search_count", [[["order_id", "=", createdOrderId]]]);
                            if (!linesCount) {
                                await this.orm.call("sale.order", "unlink", [[createdOrderId]]);
                            }
                        }
                    } catch (e) {
                        console.warn("Cleanup after discard failed:", e);
                    }
                    this.notification.add(_t("Configurator discarded."), { type: "warning" });
                },
            });
        } catch (error) {
            this.notification.add(_t("An error occurred. Please try again."), { type: "danger" });
            console.error(error);
        } finally {
            await this.env.services.ui.unblock();
        }
    },

    

    // async _cpqConfigureDialog(result = null) {
    //     if (result && !this._isCpq(result)) return;
    //     this.skipNextProductTemplateUpdate = false;

    //     const safeRead = async (model, ids, fieldList) => {
    //         const idList = Array.isArray(ids) ? ids : [ids];
    //         const result = await this.orm.call(model, "read", [idList, fieldList]);
    //         const record = Array.isArray(result) ? result[0] : result;
    //         ["product_uom", "product_id", "order_id", "product_template_id", "currency_id", "company_id"].forEach((field) => {
    //             if (record[field]) record[field] = safeMany2One(record[field]);
    //         });
    //         return record;
    //     };

    //     let activeId = this.props.record.resId || null;
    //     let orderId = this.props.record.data.order_id?.[0] || this.props.record.model.root.resId || null;
    //     const productTemplateId = safeMany2One(this.props.record.data.product_template_id)[0];
    //     let partnerIdRaw = this.props.record.data.partner_id?.[0] || this.props.record.data.order_partner_id?.[0] || null;
    //     if (!partnerIdRaw && orderId) {
    //         try {
    //             const [order] = await this.orm.call("sale.order", "read", [[orderId], ["partner_id"]]);
    //             partnerIdRaw = order?.partner_id?.[0] || null;
    //         } catch (e) { }
    //     }
    //     const partnerId = typeof partnerIdRaw === "number" && partnerIdRaw > 0 ? partnerIdRaw : null;
    //     let isVirtual = activeId && typeof activeId === "string" && activeId.startsWith("virtual");

    //     if (!productTemplateId || !orderId) {
    //         this.notification.add(_t("Cannot open configurator: missing product template or order ID."), { type: "danger" });
    //         return;
    //     }

    //     const safeFrontendUpdate = async (record, backendData) => {
    //         const frontendFields = Object.keys(record.data || {});
    //         const safeData = {};
    //         for (const [key, value] of Object.entries(backendData)) {
    //             if (frontendFields.includes(key)) safeData[key] = value;
    //         }
    //         if (backendData.id && !record.resId) safeData.id = backendData.id;
    //         if (Object.keys(safeData).length > 0) await record.update(safeData);
    //     };

    //     this.notification.add(_t("Preparing your configuration..."), { type: "info" });
    //     try {
    //         if (!activeId || isVirtual) {
    //             const { product_id } = await this.orm.call("product.template", "ensure_configurator_product", [productTemplateId]);
    //             const { uom_id } = await safeRead("product.template", productTemplateId, ["uom_id"]);
    //             const createdId = await this.orm.call("sale.order.line", "create", [{
    //                 order_id: orderId,
    //                 product_template_id: productTemplateId,
    //                 product_id: product_id,
    //                 product_uom: uom_id[0],
    //                 product_uom_qty: 1,
    //                 name: "Custom Line",
    //                 price_unit: 0.0,
    //             }]);
    //             activeId = Array.isArray(createdId) ? createdId[0] : createdId;
    //             const lineData = await safeRead("sale.order.line", activeId, [
    //                 "order_id", "product_template_id", "product_uom_qty", "currency_id", "company_id", "name", "product_uom", "product_id"
    //             ]);
    //             await safeFrontendUpdate(this.props.record, lineData);
    //             this.notification.add(_t("Order line created! Opening configurator..."), { type: "success" });
    //             this._pulseLine(activeId);
    //             isVirtual = false;
    //         }

    //         const isEdit = activeId && typeof activeId === "number" && !isVirtual;

    //         let preferences = {};
    //         if (partnerId && productTemplateId) {
    //             try {
    //                 preferences = await jsonrpc("/cpq/preferences/resolve", {
    //                     partner_id: partnerId,
    //                     product_template_id: productTemplateId,
    //                 });
    //             } catch (e) { }
    //         }

    //         const rawConfig = this.props.record.data.cpq_configuration_json;
    //         let baseConfig = {};
    //         try {
    //             baseConfig = typeof rawConfig === "string" ? JSON.parse(rawConfig) : (rawConfig || {});
    //         } catch (e) { }

    //         let selected = baseConfig.selected;
    //         if (isEmptySelected(selected)) {
    //             if (baseConfig.grouped && Object.keys(baseConfig.grouped).length) {
    //                 const flat = flattenGroupedSelection(baseConfig.grouped || {});
    //                 selected = mergeSelectedWithFallback(flat, {});
    //                 console.warn("🩹 Reconstructed selected from grouped for edit:", selected);
    //             } else {
    //                 selected = { left: {}, right: {}, shared: {} };
    //             }
    //         }
    //         if (!isEdit && preferences.selected) {
    //             selected = mergeSelectedWithFallback(selected || {}, preferences.selected || {});
    //         }

    //         const ptalData = await jsonrpc(`/cpq_product_configurator/${productTemplateId}/data`, {});
    //         console.log('[CPQ] isEdit:', isEdit, 'selected:', selected, 'baseConfig:', baseConfig, 'preferences:', preferences);

    //         this.dialogService.add(ConfigureDialog, {
    //             ptalIds: ptalData?.ptal_ids || [],
    //             record: this.props.record,
    //             orderId,
    //             activeId,
    //             partnerId,
    //             productTemplateId,
    //             edit: isEdit,
    //             cpqInitialConfig: baseConfig,
    //             initialSelected: selected,
    //             laterality: baseConfig.laterality ?? preferences.laterality ?? "bilateral",
    //             cpqPreferences: preferences,
    //             close: () => this.notification.add(_t("Configurator closed."), { type: "info" }),
    //             discard: () => this.notification.add(_t("Configurator discarded."), { type: "warning" }),
    //         });
    //     } catch (error) {
    //         this.notification.add(_t("An error occurred. Please try again."), { type: "danger" });
    //         console.error(error);
    //     } finally {
    //         await this.env.services.ui.unblock();
    //     }
    // },

    _pulseLine(lineId) {
        setTimeout(() => {
            const lineEl = document.querySelector(`[data-id="${lineId}"]`);
            if (lineEl) {
                lineEl.scrollIntoView({ behavior: "smooth", block: "center" });
                lineEl.classList.add("highlight-success");
                setTimeout(() => lineEl.classList.remove("highlight-success"), 1500);
            }
            const totalEl = document.querySelector(".o_sale_order_total");
            if (totalEl) {
                totalEl.classList.add("highlight-success");
                setTimeout(() => totalEl.classList.remove("highlight-success"), 1500);
            }
        }, 300);
    },

});