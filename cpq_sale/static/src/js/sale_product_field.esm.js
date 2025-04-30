
/** @odoo-module **/
/* eslint-disable sort-imports */

import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { useService } from "@web/core/utils/hooks";
import { ConfigureDialog } from "@cpq/components/dialog/dialog.esm";
import { _t } from "@web/core/l10n/translation";
import { getSafeConfiguratorValues, safeMany2One } from "@cpq/components/dialog/utils.esm";

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
            "product.template",
            "get_single_product_variant",
            [templateId],
            { context: this.context }
        );
    
        console.log("🟢 Resolved product variant:", result);
    
        if (this._isCpq(result)) {
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
            console.warn("❌ Unexpected product resolution result:", result);
            this.notification.add("No variant found or invalid CPQ mode.", { type: "danger" });
        }
    },
    

    // async _onProductTemplateUpdate() {
    //     if (this.skipNextProductTemplateUpdate) {
    //         this.skipNextProductTemplateUpdate = false;
    //         return;
    //     }

    //     const result = await this.orm.call(
    //         "product.template",
    //         "get_single_product_variant",
    //         [this.props.record.data.product_template_id[0]],
    //         { context: this.context }
    //     );

    //     console.log("🟢 Resolved product variant:", result);

    //     if (this._isBackendCpq(result) && this._isFrontendCpq()) {
    //         console.log("✅ CPQ product detected — opening configurator dialog.");
    //         return this._cpqConfigureDialog(result);
    //     }

    //     if (result && result.product_id) {
    //         await this.props.record.update({
    //             product_id: Array.isArray(result.product_id) ? result.product_id : [result.product_id, result.product_name],
    //             product_uom: safeMany2One(result.uom_id),
    //             price_unit: result.price_unit,
    //         });
    //         await this._onProductUpdate();
    //     } else {
    //         this.notification.add("No variant found for this product. Please check the template.", { type: "danger" });
    //     }
    // },

    async _onProductUpdate() {
        if (this._isFrontendCpq()) {
            console.log("⚙️ CPQ Product selected — skipping native product update handling.");
            return; // ✅ Skip native logic entirely
        }
    
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
        if (this._isFrontendCpq()) {
            console.log("⚙️ CPQ Product selected — skipping onProductChange.");
            return;
        }
    
        return super.onProductChange(...arguments);
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
    
        let activeId = this.props.record.resId || null;
        let orderId = this.props.record.model.root.resId || null;
        const productTmplId = safeMany2One(this.props.record.data.product_template_id)[0];
        const isVirtual = activeId && typeof activeId === "string" && activeId.startsWith("virtual");
    
        if (!productTmplId || !orderId) {
            this.notification.add("Cannot open configurator: missing product template or order ID.", { type: "danger" });
            return;
        }
    
        const safeFrontendUpdate = async (record, backendData) => {
            const frontendFields = Object.keys(record.data || {});
            const safeData = { id: activeId };
            const skippedFields = [];
    
            for (const [key, value] of Object.entries(backendData)) {
                if (frontendFields.includes(key)) safeData[key] = value;
                else skippedFields.push(key);
            }
            if (skippedFields.length) console.warn(`🚧 Skipped fields (not in view):`, skippedFields);
            if (Object.keys(safeData).length > 0) await record.update(safeData);
        };
    
        this.notification.add(_t("🔧 Preparing your configuration..."), { type: "info" });
    
        try {
            await this.env.services.ui.block();
    
            if (!activeId || isVirtual) {
                const { product_id } = await this.orm.call("product.template", "ensure_configurator_product", [productTmplId]);
                const { uom_id } = await safeRead("product.template", productTmplId, ["uom_id"]);
    
                const createdId = await this.orm.call("sale.order.line", "create", [{
                    order_id: orderId,
                    product_template_id: productTmplId,
                    product_id: product_id,
                    product_uom: uom_id[0],
                    product_uom_qty: 1,
                    name: "Custom CPQ Line",
                    price_unit: 0.0,
                }]);
    
                activeId = Array.isArray(createdId) ? createdId[0] : createdId;
    
                const lineData = await safeRead("sale.order.line", activeId, [
                    "order_id", "product_template_id", "product_uom_qty",
                    "currency_id", "company_id", "name", "product_uom", "product_id"
                ]);
    
                await safeFrontendUpdate(this.props.record, lineData);
    
                this.notification.add(_t("✅ Order line created! Opening configurator..."), { type: "success" });
                this._pulseLine(activeId);
            }
    
            const initialConfig = this.props.record.data.cpq_configuration_json
                ? JSON.parse(this.props.record.data.cpq_configuration_json)
                : {};
    
            this.dialogService.add(ConfigureDialog, {
                record: this.props.record,
                orderId,
                productTmplId,
                edit: true,
                cpqInitialConfig: initialConfig,
                save: async (configResult) => {
                    this.skipNextProductTemplateUpdate = true;
                    const updatedValues = getSafeConfiguratorValues(configResult.configuration, this.props.productUOMId);
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
