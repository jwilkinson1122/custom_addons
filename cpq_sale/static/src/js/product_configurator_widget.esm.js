/** @odoo-module **/
/* eslint-disable sort-imports */

import { ConfigureDialog } from "@cpq/components/dialog/dialog.esm";
import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { useService } from "@web/core/utils/hooks";
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

    _cpqConfigureDialog() {
        this.notification.add(_t("Opening CPQ Configurator..."), { type: "info" });

        const safeMany2One = (field) => Array.isArray(field) ? field[0] : undefined;

        const productTmplId =
            safeMany2One(this.props.record.data.product_template_id) ||
            safeMany2One(this.props.record.data.product_id);

        if (!productTmplId) {
            this.notification.add(_t("Missing product template for CPQ configuration."), { type: "danger" });
            return;
        }

        this.dialog.add(ConfigureDialog, {
            record: this.props.record,
            orderId: safeMany2One(this.props.record.data.order_id),
            productTmplId: productTmplId,
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
                        'product_id', 'name', 'price_unit', 'cpq_configuration_summary',
                    ]);
                    await this.props.record.update({
                        product_id: [lineData.product_id[0], lineData.product_id[1]],
                        name: lineData.cpq_configuration_summary || lineData.name,
                        price_unit: lineData.price_unit,
                    });
                }

                this.props.record.model.root.data.order_line.leaveEditMode();
                window.location.reload();

                if (lineId) {
                    setTimeout(() => {
                        const lineEl = document.querySelector(`[data-id="${lineId}"]`);
                        if (lineEl) {
                            lineEl.scrollIntoView({ behavior: "smooth", block: "center" });
                            lineEl.classList.add("o_selected_row");
                        }
                    }, 500);
                }
            },

            discard: () => {
                this.props.record.model.root.data.order_line.delete(this.props.record);
            },

            close: () => {
                console.log("Dialog closed");
            },
        });
    },
});