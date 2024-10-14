/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from '@web/core/registry';
import { Many2OneField, many2OneField } from '@web/views/fields/many2one/many2one_field';
import { ProductMatrixDialog } from "@product_matrix/js/product_matrix_dialog";
import { useService } from "@web/core/utils/hooks";
import { useRecordObserver } from "@web/model/relational_model/utils";

export class StockMoveLineProductField extends Many2OneField {

    setup() {
        super.setup();
        this.dialog = useService("dialog");
        this.currentValue = this.value;

        useRecordObserver((record) => {
            if (record.isInEdition && this.value) {
                if (!this.currentValue || this.currentValue[0] != record.data[this.props.name][0]) {
                    // Field was updated if line was open in edit mode,
                    //      field is not emptied,
                    //      new value is different than existing value.

                    this._onProductTemplateUpdate();
                }
            }
            this.currentValue = record.data[this.props.name];
        });
    }

    get configurationButtonHelp() {
        return _t("Edit Configuration");
    }
    get isConfigurableTemplate() {
        return this.props.record.data.is_configurable_product;
    }
    get product_mode() {
        return this.props.record.data.inventory_product_add_mode;
    }
      async _onProductTemplateUpdate() {
        if (this.props.record.resModel === 'stock.move' && this.props.record.data.inventory_product_add_mode == 'product_configurator' || this.props.record.data.inventory_product_add_mode == 'matrix' ){
                this._openGridConfigurator(false)
            }
        else {
             const result = await this.orm.call(
                'product.template',
                'get_single_product_variant',
                [this.props.record.data.product_template_id[0]],
            );
            if(result && result.product_id) {
                if (this.props.record.data.product_id != result.product_id.id) {
                    this.props.record.update({
                        // TODO right name get (same problem as configurator)
                        product_id: [result.product_id, result.product_name],
                    });
                }
            } else {
                return true;
            }
        }

      }

    onEditConfiguration() {
        if (this.product_mode !== 'normal') {
            this._openGridConfigurator(true);
        }
    }

    async _openGridConfigurator(edit) {
        const StockMoveRecord = this.props.record.model.root;

        // fetch matrix information from server;
        await StockMoveRecord.update({
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
            StockMoveRecord.data.grid,
            this.props.record.data.product_template_id[0],
            updatedLineAttributes,
        );

        if (!edit) {
            // remove new line used to open the matrix
            StockMoveRecord.data.move_ids_without_package.delete(this.props.record);
        }
    }

    _openMatrixConfigurator(jsonInfo, productTemplateId, editedCellAttributes) {
        const infos = JSON.parse(jsonInfo);
        this.dialog.add(ProductMatrixDialog, {
            header: infos.header,
            rows: infos.matrix,
            editedCellAttributes: editedCellAttributes.toString(),
            product_template_id: productTemplateId,
            record: this.props.record.model.root,
        });
    }
}

StockMoveLineProductField.template = "stock.StockProductField";

export const stockMoveLineProductField = {
    ...many2OneField,
    component: StockMoveLineProductField,
};

registry.category("fields").add("sml_product_many2one", stockMoveLineProductField);
