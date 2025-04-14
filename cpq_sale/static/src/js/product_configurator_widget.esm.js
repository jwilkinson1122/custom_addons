/** @odoo-module **/
/* eslint-disable sort-imports */

import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { useService } from "@web/core/utils/hooks";
import { ConfigureDialog } from "@cpq/components/dialog/dialog.esm";
import { serializeDateTime } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";


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
    
        const safeFrontendUpdate = async (record, backendData) => {
            const frontendFields = Object.keys(record.data || {});
            const safeData = {};
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
        let activeId = this.props.record.resId || null;

        this.notification.add(_t("🔧 Preparing your configuration..."), { type: "info" });
    
        let lineData = null;
    
        const isVirtual = activeId && typeof activeId === 'string' && activeId.startsWith('virtual');
        console.log(`🧩 _cpqConfigureDialog() invoked - Order ID: unknown yet, Order Line ID: ${activeId} (virtual: ${isVirtual})`);
    
        if (!activeId || isVirtual) {
            try {
                orderId = safeMany2One(this.props.record.model.root.resId)[0];
                if (!orderId) {
                    this.notification.add(_t("Cannot configure: missing order. Please check your order."), { type: "danger" });
                    return;
                }
    
                await this.orm.call("product.template", "ensure_configurator_product", [productTmplId]);
                const productData = await safeRead("product.template", productTmplId, ["uom_id", "product_variant_id", "name"]);
                console.log("🧩 Product data loaded:", productData);
    
                const createdId = await this.orm.call("sale.order.line", "create", [{
                    order_id: orderId,
                    product_template_id: productTmplId,
                    product_id: productData.product_variant_id?.[0] || false,
                    product_uom: productData.uom_id?.[0] || false,
                    product_uom_qty: 1,
                    name: "Custom CPQ Line",
                    price_unit: 0.0,
                }]);
    
                activeId = Array.isArray(createdId) ? createdId[0] : createdId;
                console.log("✅ Created order line ID:", activeId);
    
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
    
            } catch (error) {
                console.error("❌ Failed to create order line:", error);
                this.notification.add(_t("Failed to create order line. Please try again."), { type: "danger" });
                return;
            }
        } else {
            try {
                lineData = await safeRead("sale.order.line", activeId, ["order_id"]);
                orderId = safeMany2One(lineData?.order_id)[0] || safeMany2One(this.props.record.data.order_id)[0] || safeMany2One(this.props.record.model.root.resId)[0];
                console.log("🧩 Cached orderId from existing line:", orderId);
            } catch (error) {
                console.warn("⚠️ Could not fetch orderId from existing line:", error);
            }
        }
    
        if (!orderId) {
            console.error("🚨 orderId still undefined before opening dialog!");
            this.notification.add(_t("Cannot open configurator: missing order ID."), { type: "danger" });
            return;
        }

        console.log("🚀 Opening configurator dialog with orderId:", orderId);
        
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
                ...this.props.record.model.root.context,
                active_model: "sale.order.line",
                active_id: activeId,
                active_sale_order_id: orderId,
            },
            edit: true,
            save: async (configResult) => {
                const activeId = this.props.record.resId;
                const values = configResult.configuration;
            
                console.log("🧩 Saving CPQ configuration in _cpqConfigureDialog:", values);
            
                await this.orm.call("sale.order.line", "onchange", [activeId, values]);
                await this.orm.call("sale.order.line", "write", [activeId, values]);
            
                // 🧹 Clean up ghost frontend records (CRITICAL FIX)
                const orderLineData = this.props.record.model.root.data.order_line;
                if (orderLineData && orderLineData.records) {
                    orderLineData.records = orderLineData.records.filter(line => line.resId === activeId);
                    orderLineData.leaveEditMode();
                }
            
                this.notification.add("✅ Configuration applied successfully.", { type: "success" });
            },
            
            // save: async (configResult) => {
            //     const activeId = this.props.record.resId;
            //     const values = configResult.configuration;
            
            //     console.log("🧩 Saving CPQ configuration in _cpqConfigureDialog:", values);
            
            //     await this.orm.call("sale.order.line", "onchange", [activeId, values]);
            //     await this.orm.call("sale.order.line", "write", [activeId, values]);
            
            //     this.props.record.model.root.data.order_line.leaveEditMode();
            //     this.notification.add("✅ Configuration applied successfully.", { type: "success" });
            // },
            
            close: () => {
                this.notification.add(_t("Configurator closed."), { type: "info" });
            },
        });
        
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
