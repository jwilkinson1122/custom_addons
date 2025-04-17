/** @odoo-module **/
/* eslint-disable sort-imports */

import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { useService } from "@web/core/utils/hooks";
import { ConfigureDialog } from "@cpq/components/dialog/dialog.esm";
import { serializeDateTime } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
import { cleanGhostRecords } from "@cpq/components/dialog/utils.esm";

patch(SaleOrderLineProductField.prototype, {
    setup() {
        super.setup(...arguments);
        this.dialogService = useService("dialog");
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.skipNextProductTemplateUpdate = false;
    },

    _editProductConfiguration() {
        if (this.props.record.data.product_template_id_cpq_ok) {
            const orderId = this.props.record.model.root.resId || null;
            console.log("🚀 Opening configurator dialog with orderId:", orderId);
            return this._cpqConfigureDialog();
        }
        super._editProductConfiguration(...arguments);
    },
    
    async _openProductConfigurator(edit = false) {
        if (edit && this.props.record.data.product_template_id_cpq_ok) {
            return this._cpqConfigureDialog();
        }
        super._openProductConfigurator(...arguments);
    },

    async _onProductTemplateUpdate() {
        if (this.skipNextProductTemplateUpdate) {
            this.skipNextProductTemplateUpdate = false;
            return;
        }

        if (this.props.record.data.product_template_id_cpq_ok) {
            return this._cpqConfigureDialog();
        }

        super._onProductTemplateUpdate(...arguments);
    },

    async _cpqConfigureDialog() {
        this.skipNextProductTemplateUpdate = false;
    
        const safeMany2One = (field) => Array.isArray(field) ? field : field ? [field, ""] : [false, ""];
        const safeRead = async (model, ids, fieldList) => {
            try {
                const idList = Array.isArray(ids) ? ids : [ids];
                const result = await this.orm.call(model, "read", [idList, fieldList]);
                return Array.isArray(result) ? result[0] : result;
            } catch (error) {
                console.error(`❌ Failed to read model: ${model} with ID(s): ${ids}`, error);
                throw error;
            }
        };
    
        let activeId = this.props.record.resId || null;
        let orderId = this.props.record.model.root.resId || null;
        const productTmplId = safeMany2One(this.props.record.data.product_template_id)[0];
        const isVirtual = activeId && typeof activeId === 'string' && activeId.startsWith('virtual');
    
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
    
        if (!productTmplId) {
            this.notification.add(_t("Missing product template for CPQ configuration."), { type: "danger" });
            return;
        }
    
        this.notification.add(_t("🔧 Preparing your configuration..."), { type: "info" });

        let productData = null;  

        try {
            await this.env.services.ui.block();
    
            if (!activeId || isVirtual) {
                if (!orderId) {
                    this.notification.add(_t("Cannot configure: missing order. Please check your order."), { type: "danger" });
                    return;
                }
    
                await this.orm.call("product.template", "ensure_configurator_product", [productTmplId]);

                productData = await safeRead("product.template", productTmplId, [
                    "uom_id",
                    "product_variant_id",
                    "name",
                    "display_name",
                    "image_128",
                    "list_price",
                    "description_sale",
                ]);
                
                if (!productData.product_variant_id?.[0] || !productData.uom_id?.[0]) {
                    const missing = !productData.product_variant_id?.[0] ? "product variant ID" : "Unit of Measure (UoM)";
                    this.notification.add(_t(`Cannot configure: Missing ${missing} from product template.`), { type: "danger" });
                    await this.env.services.ui.unblock();
                    return;
                }
    
                const createdId = await this.orm.call("sale.order.line", "create", [{
                    order_id: orderId,
                    product_template_id: productTmplId,
                    product_id: productData.product_variant_id[0],
                    product_uom: productData.uom_id[0],
                    product_uom_qty: 1,
                    name: "Custom CPQ Line",
                    price_unit: 0.0,
                }]);
    
                activeId = Array.isArray(createdId) ? createdId[0] : createdId;
                await this.orm.call("sale.order.line", "read", [[activeId], ["id"]]);
    
                const lineData = await safeRead("sale.order.line", activeId, [
                    "order_id", "product_template_id", "product_uom_qty",
                    "currency_id", "company_id", "name", "product_uom",
                ]);
    
                orderId = safeMany2One(lineData.order_id)[0] || orderId;
    
                await safeFrontendUpdate(this.props.record, {
                    order_id: safeMany2One(lineData.order_id),
                    product_template_id: safeMany2One(lineData.product_template_id),
                    product_uom_qty: lineData.product_uom_qty,
                    currency_id: safeMany2One(lineData.currency_id),
                    company_id: safeMany2One(lineData.company_id),
                    name: lineData.name,
                    product_uom: safeMany2One(lineData.product_uom),
                });
    
                this.notification.add(_t("✅ Order line created! Opening configurator..."), { type: "success" });
                this._pulseLine(activeId);
            } else {
                const lineData = await safeRead("sale.order.line", activeId, ["order_id"]);
                orderId = safeMany2One(lineData?.order_id)[0] || orderId;
                productData = await safeRead("product.template", safeMany2One(lineData.product_template_id)[0], [
                    "uom_id",
                    "product_variant_id",
                    "name",
                    "display_name",
                    "image_128",
                    "list_price",
                    "description_sale",
                ]);
            }
    
            const orderModel = this.props.record?.model?.root;
            if (orderModel?.data?.order_line?.records) {
                orderModel.data.order_line.records = orderModel.data.order_line.records.filter(line => {
                    if (typeof line.resId === 'string' && line.resId.startsWith('virtual')) {
                        console.warn(`🧹 Removing virtual order line: ${line.resId}`);
                        return false;
                    }
                    return true;
                });
                orderModel.data.order_line.leaveEditMode?.();
            }
    
            let initialConfig = {};
            try {
                const raw = this.props.record.data.cpq_configuration_json;
                if (raw) initialConfig = typeof raw === "string" ? JSON.parse(raw) : raw;
            } catch (e) {
                console.warn("⚠️ Failed to parse cpq_configuration_json:", e);
            }
            console.log("✅ Final productData:", productData);

            this.dialogService.add(ConfigureDialog, {
                record: this.props.record,
                orderId,
                productTmplId: productData.id,
                productTemplate: productData,
                quantity: this.props.record.data.product_uom_qty,
                currencyId: safeMany2One(this.props.record.data.currency_id)[0],
                soDate: serializeDateTime(this.props.record.model.root.data.date_order),
                productUOMId: safeMany2One(this.props.record.data.product_uom)[0],
                companyId: safeMany2One(this.props.record.model.root.data.company_id)[0],
                context: {
                    active_model: "sale.order.line",
                    active_id: activeId,
                    active_sale_order_id: orderId,
                    ...(this.props.record?.model?.root?.context || {}),
                },
                cpqInitialConfig: initialConfig,
                edit: true,
                save: async (configResult) => {
                    this.skipNextProductTemplateUpdate = true;
                    const configValues = configResult.configuration;
                    const safeLineData = await safeRead("sale.order.line", activeId, [
                        "product_id", "product_uom", "product_template_id", "currency_id",
                        "company_id", "name", "product_uom_qty", "price_unit", "cpq_configuration_json",
                    ]);
    
                    const values = {
                        ...configValues,
                        product_id: safeMany2One(safeLineData.product_id)[0],
                        product_uom: safeMany2One(safeLineData.product_uom)[0],
                        product_template_id: safeMany2One(safeLineData.product_template_id)[0],
                        currency_id: safeMany2One(safeLineData.currency_id)[0],
                        company_id: safeMany2One(safeLineData.company_id)[0],
                        name: safeLineData.name || configValues.name,
                        product_uom_qty: safeLineData.product_uom_qty || 1,
                    };
    
                    await this.orm.call("sale.order.line", "onchange", [activeId, values]);
                    await this.orm.call("sale.order.line", "write", [activeId, values]);
    
                    this.notification.add("✅ Configuration applied successfully.", { type: "success" });
                },
                close: () => this.notification.add(_t("Configurator closed."), { type: "info", title: "CPQ Close" }),
                discard: () => this.notification.add(_t("Configurator discarded."), { type: "warning", title: "CPQ Cancelled" })
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
