/** @odoo-module **/
/* eslint-disable sort-imports */

import {ConfigureDialog} from "@cpq/components/dialog/dialog.esm";
import { patch } from "@web/core/utils/patch";
import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {useService} from "@web/core/utils/hooks";
import { serializeDateTime } from "@web/core/l10n/dates";


// export async function applyProduct(record, configResult) {
//     console.log("🧩 Applying configured product to order line:", configResult);

//     if (!record) {
//         console.warn("⚠️ No record provided to applyProduct.");
//         return;
//     }

//     const updates = {
//         product_id: [configResult.product_id, configResult.product_display_name],
//         cpq_configuration_json: configResult.configuration_json,
//         cpq_configuration_summary: configResult.configuration_summary,
//         product_uom_qty: configResult.configuration?.quantity_to_make || 1,
//         // 👉 Add more fields if needed, like pricing, currency, etc.
//     };

//     console.log("💾 Applying updates to record:", updates);

//     await record.update(updates);

//     // Ensure UI refresh
//     record.model.root.data.order_line.leaveEditMode();

//     console.log("✅ Order line updated with CPQ configuration.");
// }

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

    // async _onProductTemplateUpdate() {
    //     if (this.props.record.data.product_template_id_cpq_ok) {
    //         return this._cpqConfigureDialog();
    //     }
    //     super._onProductTemplateUpdate(...arguments);
    // },

    _cpqConfigureDialog() {
        const safeMany2One = (field) => Array.isArray(field) ? field[0] : undefined;
    
        this.dialog.add(ConfigureDialog, {
            record: this.props.record,
            orderId: safeMany2One(this.props.record.data.order_id),
            productTmplId: safeMany2One(this.props.record.data.product_template_id),
            quantity: this.props.record.data.product_uom_qty,
            currencyId: safeMany2One(this.props.record.data.currency_id),
            soDate: serializeDateTime(this.props.record.model.root.data.date_order),
            productUOMId: safeMany2One(this.props.record.data.product_uom),
            pricelistId: safeMany2One(this.props.record.model.root.data.pricelist_id),
            companyId: safeMany2One(this.props.record.model.root.data.company_id),
            edit: true,
            save: async (productTmplId, result) => {
                const lineId = result.sale_order_line_id;
                // ✅ Before updating, prevent trigger loop
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
                } else {
                    console.warn("⚠️ No sale_order_line_id returned from configurator backend");
                }
                this.props.record.model.root.data.order_line.leaveEditMode();
            },
            discard: () => {
                this.props.record.model.root.data.order_line.delete(this.props.record);
            },
            close: () => {
                console.log("Dialog closed");
            },
        });
    }
    

    // _cpqConfigureDialog() {
    //     const orderId = this.props.record.data.order_id ? this.props.record.data.order_id[0] : undefined;

    //     this.dialog.add(ConfigureDialog, {
    //         record: this.props.record,
    //         orderId: orderId,
    //         productTmplId: this.props.record.data.product_template_id[0],
    //         quantity: this.props.record.data.product_uom_qty,
    //         currencyId: this.props.record.data.currency_id[0],
    //         soDate: serializeDateTime(this.props.record.model.root.data.date_order),
    //         productUOMId: this.props.record.data.product_uom[0],
    //         pricelistId: this.props.record.model.root.data.pricelist_id[0],
    //         companyId: this.props.record.model.root.data.company_id[0],
    //         edit: true,
    //         save: async (productTmplId, result) => {
    //             const lineId = result.sale_order_line_id;
    //             if (lineId) {
    //                 const [lineData] = await this.orm.call('sale.order.line', 'read', [lineId], [
    //                     'product_id',
    //                     'name',
    //                     'price_unit',
    //                     'cpq_configuration_summary',
    //                 ]);
    //                 await this.props.record.update({
    //                     product_id: [lineData.product_id[0], lineData.product_id[1]],
    //                     name: lineData.cpq_configuration_summary || lineData.name,
    //                     price_unit: lineData.price_unit,
    //                 });
    //             } else {
    //                 console.warn("⚠️ No sale_order_line_id returned from configurator backend");
    //             }
    //             this.props.record.model.root.data.order_line.leaveEditMode();
    //         },
    //         discard: () => {
    //             this.props.record.model.root.data.order_line.delete(this.props.record);
    //         },
    //         close: () => {
    //             console.log("Dialog closed");
    //         },
    //     });
    // }
    
});
