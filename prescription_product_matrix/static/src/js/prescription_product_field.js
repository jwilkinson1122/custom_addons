/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PrescriptionLineProductField } from '@prescription/js/prescription_product_field';
import { ProductMatrixDialog } from "@product_matrix/js/product_matrix_dialog";
import { useService } from "@web/core/utils/hooks";
import "@prescription_product_configurator/js/prescription_product_field";


patch(PrescriptionLineProductField.prototype, {

    setup() {
        super.setup(...arguments);
        this.dialog = useService("dialog");
    },

    async _openGridConfigurator(edit=false) {
        const prescriptionOrderRecord = this.props.record.model.root;

        // fetch matrix information from server;
        await prescriptionOrderRecord.update({
            grid_product_tmpl_id: this.props.record.data.product_template_id,
        });

        let updatedLineAttributes = [];
        if (edit) {
            // provide attributes of edited line to automatically focus on matching cell in the matrix
            for (let ptnvav of this.props.record.data.product_no_variant_attribute_value_ids.records) {
                updatedLineAttributes.push(ptnvav.resId);
            }
            for (let ptav of this.props.record.data.product_template_attribute_value_ids.records) {
                updatedLineAttributes.push(ptav.resId);
            }
            updatedLineAttributes.sort((a, b) => { return a - b; });
        }

        this._openMatrixConfigurator(
            prescriptionOrderRecord.data.grid,
            this.props.record.data.product_template_id[0],
            updatedLineAttributes,
        );

        if (!edit) {
            // remove new line used to open the matrix
            prescriptionOrderRecord.data.order_line.delete(this.props.record);
        }
    },

    async _openProductConfigurator(edit=false) {
        if (edit && this.props.record.data.product_add_mode == 'matrix') {
            this._openGridConfigurator(true);
        } else {
            super._openProductConfigurator(...arguments);
        }
    },

    /**
     * Triggers Matrix Dialog opening
     *
     * @param {String} jsonInfo matrix dialog content
     * @param {integer} productTemplateId product.template id
     * @param {editedCellAttributes} list of product.template.attribute.value ids
     *  used to focus on the matrix cell representing the edited line.
     *
     * @private
    */
    _openMatrixConfigurator(jsonInfo, productTemplateId, editedCellAttributes) {
        const infos = JRXN.parse(jsonInfo);
        this.dialog.add(ProductMatrixDialog, {
            header: infos.header,
            rows: infos.matrix,
            editedCellAttributes: editedCellAttributes.toString(),
            product_template_id: productTemplateId,
            record: this.props.record.model.root,
        });
    },
});
