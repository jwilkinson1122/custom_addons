
/** @odoo-module **/
/* eslint-disable sort-imports */

import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { useService } from "@web/core/utils/hooks";
import { ConfigureDialog } from "./dialog.esm";
import { _t } from "@web/core/l10n/translation";
import { getSafeConfiguratorValues, safeMany2One } from "./utils.esm";

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

        const result = await this.orm.call(
            "product.template",
            "get_single_product_variant",
            [this.props.record.data.product_template_id[0]],
            { context: this.context }
        );

        console.log("🟢 Resolved product variant:", result);

        if (this._isBackendCpq(result) && this._isFrontendCpq()) {
            console.log("✅ CPQ product detected — opening configurator dialog.");
            return this._cpqConfigureDialog(result);
        }

        if (result && result.product_id) {
            await this.props.record.update({
                product_id: Array.isArray(result.product_id) ? result.product_id : [result.product_id, result.product_name],
                product_uom: safeMany2One(result.uom_id),
                price_unit: result.price_unit,
            });
            await this._onProductUpdate();
        } else {
            this.notification.add("No variant found for this product. Please check the template.", { type: "danger" });
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

    _editProductConfiguration() {
        if (this._isFrontendCpq()) {
            console.log("✅ CPQ Product detected — opening configurator.");
            return this._cpqConfigureDialog();
        }
        console.log("🛑 Non-CPQ product — using native Odoo flow.");
        return super._editProductConfiguration(...arguments);
    },

    async _openProductConfigurator(edit = false) {
        if (!this._isFrontendCpq()) {
            return super._openProductConfigurator(...arguments);
        }
        return this._cpqConfigureDialog();
    },

    async _cpqConfigureDialog(result = null) {
        if (result && !this._isCpq(result)) {
            console.warn("❌ Tried to open CPQ configurator for a non-CPQ product. Aborting.");
            return;
        }
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
    
        let lineId = this.props.record.resId || null;
        let orderId = this.props.record.model.root.resId || null;
        const productTmplId = safeMany2One(this.props.record.data.product_template_id)[0];
        const isVirtual = lineId && typeof lineId === "string" && lineId.startsWith("virtual");
    
        if (!productTmplId || !orderId) {
            this.notification.add("Cannot open configurator: missing product template or order ID.", { type: "danger" });
            return;
        }
    
        const safeFrontendUpdate = async (record, backendData) => {
            const frontendFields = Object.keys(record.data || {});
            const safeData = { id: lineId };
            const skippedFields = [];
        
            for (const [key, value] of Object.entries(backendData)) {
                if (frontendFields.includes(key)) safeData[key] = value;
                else skippedFields.push(key);
            }
            if (backendData.display_type === "line_section") {
                delete safeData.product_id;
                delete safeData.product_template_id;
                delete safeData.product_uom;
            }
            if (skippedFields.length) console.warn(`🚧 Skipped fields (not in view):`, skippedFields);
            if (Object.keys(safeData).length > 0) await record.update(safeData);
        };
        
    
        this.notification.add(_t("🔧 Preparing your configuration..."), { type: "info" });
    
        try {
            await this.env.services.ui.block();
    
            if (!lineId || isVirtual) {
                const productTemplateData = await safeRead("product.template", productTmplId, ["product_variant_id", "uom_id"]);
                const productVariantId = productTemplateData.product_variant_id?.[0] || null;
                const uomId = productTemplateData.uom_id?.[0] || null;
    
                const vals = {
                    order_id: orderId,
                    product_template_id: productTmplId,
                };
    
                if (productVariantId) {
                    vals.product_id = productVariantId;
                    vals.product_uom = uomId;
                    vals.product_uom_qty = 1;
                    vals.name = "Custom CPQ Line";
                    vals.price_unit = 0.0;
                } else {
                    vals.display_type = "line_section";
                    vals.name = "CPQ Configuration Placeholder (no variant)";
                }
    
                lineId = await this.orm.call("sale.order.line", "create", [vals]);
    
                const lineData = await safeRead("sale.order.line", lineId, [
                    "order_id", "product_template_id", "product_uom_qty",
                    "currency_id", "company_id", "name", "product_uom",
                ]);
    
                await safeFrontendUpdate(this.props.record, {
                    order_id: lineData.order_id,
                    product_template_id: lineData.product_template_id,
                    product_id: lineData.product_id,
                    product_uom: lineData.product_uom,
                    currency_id: lineData.currency_id,
                    company_id: lineData.company_id,
                    name: lineData.name,
                });
    
                this.notification.add(_t("✅ Order line created! Opening configurator..."), { type: "success" });
                this._pulseLine(lineId);
            }
    
            const initialConfig = this.props.record.data.cpq_configuration_json ? JSON.parse(this.props.record.data.cpq_configuration_json) : {};
            const quantity = this.props.record.data.product_uom_qty || 1;
            const currencyId = this.props.record.data.currency_id?.[0] || null;
            const orderData = await safeRead("sale.order", orderId, ["date_order"]);
            const soDate = orderData.date_order || "";
    
            this.dialogService.add(ConfigureDialog, {
                record: this.props.record,
                orderId,
                productTmplId,
                edit: true,
                cpqInitialConfig: initialConfig,
                quantity,
                currencyId,
                soDate,
                context: {
                    active_model: "sale.order.line",
                    active_id: lineId,
                    active_sale_order_id: orderId,
                },
                save: async (configResult) => {
                    this.skipNextProductTemplateUpdate = true;
    
                    if (!configResult.configuration) {
                        console.error("❌ Missing configuration data from configurator save.");
                        this.notification.add("Configuration data missing. Please retry.", { type: "danger" });
                        return;
                    }
    
                    const updatedValues = getSafeConfiguratorValues(configResult.configuration, this.props.productUOMId);

                    updatedValues.name = configResult.configuration.name 
                        || this.props.record.data.name 
                        || "Configured Product";
                
                    if (configResult.configuration.display_type === "line_section") {
                        delete updatedValues.product_id;
                        delete updatedValues.product_template_id;
                        delete updatedValues.product_uom;
                    }
                
    
                    if (configResult.configuration_summary) {
                        updatedValues.cpq_configuration_summary = configResult.configuration_summary;
                    }
    
                    if (configResult.configuration.laterality) {
                        updatedValues.cpq_laterality = configResult.configuration.laterality;
                    }
    
                    await this.props.record.update(updatedValues);
                    this.notification.add("✅ Configuration applied successfully.", { type: "success" });
                },
                close: () => this.notification.add("Configurator closed.", { type: "info", title: "CPQ Close" }),
                discard: () => this.notification.add("Configurator discarded.", { type: "warning", title: "CPQ Cancelled" }),
            });
        } catch (error) {
            console.error("❌ Failed to open CPQ configurator:", error);
            this.notification.add("An error occurred. Please try again.", { type: "danger" });
        } finally {
            await this.env.services.ui.unblock();
        }
    },
    
    
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
