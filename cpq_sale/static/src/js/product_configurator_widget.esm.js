/** @odoo-module **/
/* eslint-disable sort-imports */

import {ConfigureDialog} from "@cpq/components/dialog/dialog.esm";
import { patch } from "@web/core/utils/patch";
import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {useService} from "@web/core/utils/hooks";
import { serializeDateTime } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";


patch(SaleOrderLineProductField.prototype, {
    setup() {
        super.setup(...arguments);
        this.dialogService = useService("dialog");
        this.notification = useService("notification");
        this.orm = useService("orm");
        
        
        // ✅ Flag to prevent re-triggering the configurator
        this.skipNextProductTemplateUpdate = false;  
    },

    _editProductConfiguration() {
        if (this.props.record.data.product_template_id_cpq_ok) {
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
            this.skipNextProductTemplateUpdate = false;  // ✅ Reset flag
            return;  // ✅ Prevent reopening configurator
        }

        if (this.props.record.data.product_template_id_cpq_ok) {
            return this._cpqConfigureDialog();
        }

        super._onProductTemplateUpdate(...arguments);
    },

    _cpqConfigureDialog() {
        this.notification.add(_t("Opening CPQ Configurator..."), {
            type: "info",
        });
    
        const safeMany2One = (field) => Array.isArray(field) ? field[0] : undefined;
    
        this.dialog.add(ConfigureDialog, {
            record: this.props.record,
            orderId: safeMany2One(this.props.record.data.order_id),
            productTmplId: safeMany2One(this.props.record.data.product_template_id),
            // productTmplId: safeMany2One(this.props.record.data.product_template_id) || safeMany2One(this.props.record.data.product_id),

            // productTmplId: safeMany2One(this.props.record.data.product_id),

            quantity: this.props.record.data.product_uom_qty,
            currencyId: safeMany2One(this.props.record.data.currency_id),
            soDate: serializeDateTime(this.props.record.model.root.data.date_order),
            productUOMId: safeMany2One(this.props.record.data.product_uom),
            pricelistId: safeMany2One(this.props.record.model.root.data.pricelist_id),
            companyId: safeMany2One(this.props.record.model.root.data.company_id),
            edit: true,
            save: async (productTmplId, result) => {
                const lineId = result.sale_order_line_id;
                this.skipNextProductTemplateUpdate = true;
            
                if (lineId) {
                    const [lineData] = await this.orm.call('sale.order.line', 'read', [lineId], [
                        'product_id',
                        'name',
                        'price_unit',
                        'cpq_configuration_summary',
                    ]);
                    await this.props.record.update({
                        product_id: [lineData.product_id[0], lineData.product_id[1]],
                        name: lineData.cpq_configuration_summary || lineData.name,
                        price_unit: lineData.price_unit,
                    });
                }
            
                this.props.record.model.root.data.order_line.leaveEditMode();
            
                // ✅ Reload to show updated configuration
                window.location.reload();
            
                // ✅ After reload, scroll to line (use location.hash trick)
                if (lineId) {
                    setTimeout(() => {
                        const lineEl = document.querySelector(`[data-id="${lineId}"]`);
                        if (lineEl) {
                            lineEl.scrollIntoView({ behavior: "smooth", block: "center" });
                            lineEl.classList.add("o_selected_row");
                        }
                    }, 500); // slight delay after reload
                }
            },
            
            discard: () => {
                this.props.record.model.root.data.order_line.delete(this.props.record);
            },
            close: () => {
                console.log("Dialog closed");
            },
        });
    }
    
});
