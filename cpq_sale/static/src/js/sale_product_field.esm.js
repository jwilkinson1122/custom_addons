/** @odoo-module **/
/* eslint-disable sort-imports */

import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { useService } from "@web/core/utils/hooks";
import { ConfigureDialog } from "@cpq/components/dialog/dialog.esm";
import { serializeDateTime } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
// C:\odoo17\server\odoo\custom_addons\cpq\static\src\components\dialog\utils.esm.js
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
        const safeFrontendUpdate = async (record, backendData) => {
            const frontendFields = Object.keys(record.data || {});
            const safeData = { id: activeId }; 
            const skippedFields = [];
        
            for (const [key, value] of Object.entries(backendData)) {
                if (frontendFields.includes(key)) {
                    safeData[key] = Array.isArray(value) ? value : value;
                } else {
                    skippedFields.push(key);
                }
            }
        
            if (skippedFields.length > 0) {
                console.warn(`🚧 Skipped fields (not in view):`, skippedFields);
            }
        
            if (Object.keys(safeData).length > 0) {
                console.log("✅ Safe data applied to record:", safeData);
                await record.update(safeData);
            }
        };
    
        const productTmplId = safeMany2One(this.props.record.data.product_template_id)[0];
        if (!productTmplId) {
            this.notification.add(_t("Missing product template for CPQ configuration."), { type: "danger" });
            return;
        }
    
        let orderId = this.props.record.model.root.resId || null;
        // let activeId = this.props.record.resId || null;
    
        this.notification.add(_t("🔧 Preparing your configuration..."), { type: "info" });
    
        let lineData = null;
    
        const isVirtual = activeId && typeof activeId === 'string' && activeId.startsWith('virtual');
        console.log(`🧩 _cpqConfigureDialog() invoked - Order ID: ${orderId}, Order Line ID: ${activeId} (virtual: ${isVirtual})`);
    
        try {
            await this.env.services.ui.block();
    
            if (!activeId || isVirtual) {
                orderId = safeMany2One(this.props.record.model.root.resId)[0];
                if (!orderId) {
                    this.notification.add(_t("Cannot configure: missing order. Please check your order."), { type: "danger" });
                    return;
                }
    
                await this.orm.call("product.template", "ensure_configurator_product", [productTmplId]);
                const productData = await safeRead("product.template", productTmplId, ["uom_id", "product_variant_id", "name"]);
                console.log("🧩 Product data loaded:", productData);
    
                if (!productData.product_variant_id?.[0]) {
                    this.notification.add(_t("Cannot configure: Missing product variant ID from template."), { type: "danger" });
                    console.error("❌ Missing product_variant_id in productData:", productData);
                    await this.env.services.ui.unblock();
                    return;
                }
                
                if (!productData.uom_id?.[0]) {
                    this.notification.add(_t("Cannot configure: Missing Unit of Measure (UoM) from product template."), { type: "danger" });
                    console.error("❌ Missing uom_id in productData:", productData);
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
                console.log("✅ Created order line ID:", activeId);

                await this.orm.call("sale.order.line", "read", [[activeId], ["id"]]);

                lineData = await safeRead("sale.order.line", activeId, [
                    "order_id",
                    "product_template_id",
                    "product_uom_qty",
                    "currency_id",
                    "company_id",
                    "name",
                    "product_uom",
                ]);
    
                orderId = safeMany2One(lineData.order_id)[0] || orderId;
                console.log("🧩 Cached orderId after creation:", orderId);
    
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
                setTimeout(() => {
                    const lineEl = document.querySelector(`[data-id="${activeId}"]`);
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
            } else {
                lineData = await safeRead("sale.order.line", activeId, ["order_id"]);
                orderId = safeMany2One(lineData?.order_id)[0] || safeMany2One(this.props.record.data.order_id)[0] || safeMany2One(this.props.record.model.root.resId)[0];
                console.log("🧩 Cached orderId from existing line:", orderId);
            }
    
            const orderModel = this.props.record?.model?.root;
            if (orderModel?.data?.order_line?.records) {
                orderModel.data.order_line.records = orderModel.data.order_line.records.filter(line => {
                    const isVirtual = typeof line.resId === 'string' && line.resId.startsWith('virtual');
                    if (isVirtual) {
                        console.warn(`🧹 Removing virtual order line: ${line.resId}`);
                    }
                    return !isVirtual;
                });
                orderModel.data.order_line.leaveEditMode?.();
                console.log("✅ Cleaned virtual lines before opening CPQ dialog");
            }


            console.log("🚀 Opening configurator dialog with orderId:", orderId);
            console.log("🧩 Launching CPQ dialog with activeId:", activeId);

            this.dialogService.add(ConfigureDialog, {
                record: this.props.record,
                orderId,
                productTmplId,
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
                
                edit: true,
    
                save: async (configResult) => {
                    const configValues = configResult.configuration;
                    const safeLineData = await safeRead("sale.order.line", activeId, [
                        "product_id",
                        "product_uom",
                        "product_template_id",
                        "currency_id",
                        "company_id",
                        "name",
                        "product_uom_qty",
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
    
                    console.log("🧩 Saving CPQ configuration with safe merged values:", values);
    
                    await this.orm.call("sale.order.line", "onchange", [activeId, values]);
                    await this.orm.call("sale.order.line", "write", [activeId, values]);
    
                    this.notification.add("✅ Configuration applied successfully.", { type: "success" });

                },
    
                close: () => {
                    this.notification.add(_t("Configurator closed."), { type: "info" });
                },

                discard: () => {
                    this.notification.add(_t("Configurator discarded."), { type: "info" });
                },
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
