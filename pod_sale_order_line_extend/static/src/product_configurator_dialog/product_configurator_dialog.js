/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Component, onWillStart, useState, useSubEnv } from "@odoo/owl";
import { Dialog } from '@web/core/dialog/dialog';
// import { ProductList } from "../product_list/product_list";
import { useService } from "@web/core/utils/hooks";
import { ProductConfiguratorDialog } from "@sale_product_configurator/js/product_configurator_dialog/product_configurator_dialog";
import { Product } from "@sale_product_configurator/js/product/product";
import { patch } from "@web/core/utils/patch";
import { x2ManyCommands } from "@web/core/orm_service";
import { SaleOrderLineProductField } from '@sale/js/sale_product_field';
import { serializeDateTime } from "@web/core/l10n/dates";
import { WarningDialog } from "@web/core/errors/error_dialogs";
import { formatCurrency } from "@web/core/currency";

async function applyProductToSaleOrder(record, product) {
    // handle custom values & no variants
    const customAttributesCommands = [
        x2ManyCommands.set([]),  // Command.clear isn't supported in static_list/_applyCommands
    ];
    for (const ptal of product.attribute_lines) {
        const selectedCustomPTAV = ptal.attribute_values.find(
            ptav => ptav.is_custom && ptal.selected_attribute_value_ids.includes(ptav.id)
        );
        if (selectedCustomPTAV) {
            customAttributesCommands.push(
                x2ManyCommands.create(undefined, {
                    custom_product_template_attribute_value_id: [selectedCustomPTAV.id, "we don't care"],
                    custom_value: ptal.customValue,
                })
            );
        };
    }

    const noVariantPTAVIds = product.attribute_lines.filter(
        ptal => ptal.create_variant === "no_variant"
    ).flatMap(ptal => ptal.selected_attribute_value_ids);

    await record.update({
        product_id: [product.id, product.display_name],
        product_uom_qty: product.quantity,
        product_no_variant_attribute_value_ids: [x2ManyCommands.set(noVariantPTAVIds)],
        product_custom_attribute_value_ids: customAttributesCommands,
        price_unit:product.price
    });

};

patch(Product.prototype,{
    setup(){
        super.setup();
    },
    updateUserPrice(e) {
        this.env.setUserPrice(this.props.product_tmpl_id, parseFloat(e.target.value),e.target);
    },
});

patch(SaleOrderLineProductField.prototype, {
    setup() {
        super.setup(...arguments);

        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.orm = useService("orm");
    },


   async _openProductConfigurator(edit=false) {
        const saleOrderRecord = this.props.record.model.root;
        let ptavIds = this.props.record.data.product_template_attribute_value_ids.records.map(
            record => record.resId
        );
        let customAttributeValues = [];

        if (edit) {
            /**
             * no_variant and custom attribute don't need to be given to the configurator for new
             * products.
             */
            ptavIds = ptavIds.concat(this.props.record.data.product_no_variant_attribute_value_ids.records.map(
                record => record.resId
            ));
            /**
             *  `product_custom_attribute_value_ids` records are not loaded in the view bc sub templates
             *  are not loaded in list views. Therefore, we fetch them from the server if the record is
             *  saved. Else we use the value stored on the line.
             */
            customAttributeValues =
                this.props.record.data.product_custom_attribute_value_ids.records[0]?.isNew ?
                this.props.record.data.product_custom_attribute_value_ids.records.map(
                    record => record.data
                ) :
                await this.orm.read(
                    'product.attribute.custom.value',
                    this.props.record.data.product_custom_attribute_value_ids.currentIds,
                    ["custom_product_template_attribute_value_id", "custom_value"]
                )
        }

        this.dialog.add(ProductConfiguratorDialog, {
            productTemplateId: this.props.record.data.product_template_id[0],
            ptavIds: ptavIds,
            customAttributeValues: customAttributeValues.map(
                data => {
                    return {
                        ptavId: data.custom_product_template_attribute_value_id[0],
                        value: data.custom_value,
                    }
                }
            ),
            quantity: this.props.record.data.product_uom_qty,
            productUOMId: this.props.record.data.product_uom[0],
            companyId: saleOrderRecord.data.company_id[0],
            pricelistId: saleOrderRecord.data.pricelist_id[0],
            currencyId: this.props.record.data.currency_id[0],
            soDate: serializeDateTime(saleOrderRecord.data.date_order),
            edit: edit,
            save: async (mainProduct, optionalProducts) => {
                if(typeof mainProduct != 'string'){
                    await applyProductToSaleOrder(this.props.record, mainProduct);
                    this._onProductUpdate();
                    saleOrderRecord.data.order_line.leaveEditMode();
                    for (const optionalProduct of optionalProducts) {
                        const line = await saleOrderRecord.data.order_line.addNewRecord({
                            position: 'bottom',
                            mode: "readonly",
                        });
                        await applyProductToSaleOrder(line, optionalProduct);
                        this._onProductUpdate();
                    }
                }else{
                    if(this.props.record.data.product_id == false){
                        for (const optionalProduct of optionalProducts) {
                            if(optionalProduct.id == optionalProducts[0].id){
                                await applyProductToSaleOrder(this.props.record, optionalProduct);
                                this._onProductUpdate();
                            }else{
                                saleOrderRecord.data.order_line.leaveEditMode();
                                const line = await saleOrderRecord.data.order_line.addNewRecord({
                                    position: 'bottom',
                                    mode: "readonly",
                                });
                                await applyProductToSaleOrder(line, optionalProduct);
                                this._onProductUpdate();
                            }
                        }
                    }else{
                        for (const optionalProduct of optionalProducts) {
                            saleOrderRecord.data.order_line.leaveEditMode();
                            const line = await saleOrderRecord.data.order_line.addNewRecord({
                                position: 'bottom',
                                mode: "readonly",
                            });
                            await applyProductToSaleOrder(line, optionalProduct);
                            this._onProductUpdate();
                        }
                    }
                }

            },
            discard: () => {
                saleOrderRecord.data.order_line.delete(this.props.record);
            },
        });
    },
});

patch(ProductConfiguratorDialog.prototype, {
    setup(){
        super.setup();
        useSubEnv({
            mainProductTmplId: this.props.productTemplateId,
            currencyId: this.props.currencyId,
            addProduct: this._addProduct.bind(this),
            removeProduct: this._removeProduct.bind(this),
            setQuantity: this._setQuantity.bind(this),
            updateProductTemplateSelectedPTAV: this._updateProductTemplateSelectedPTAV.bind(this),
            updatePTAVCustomValue: this._updatePTAVCustomValue.bind(this),
            isPossibleCombination: this._isPossibleCombination,
            setUserPrice:this._setUserPrice.bind(this)
        });
    },
    /**
     * @override
     */
    async onContinue() {
        if (this.isProcessing) {
            return; // Prevent multiple triggers
        }
        this.isCustomButton = true
        this.isProcessing = true; // Lock the function


        try {
            if (!this.isPossibleConfiguration()) {
                return;
            }
            for (const product of this.state.products) {

                if (
                    !product.id &&
                    product.attribute_lines.some(ptal => ptal.create_variant === "dynamic")
                ) {
                    const productId = await this._createProduct(product);
                    product.id = parseInt(productId);
                }
            }

            // Process sale order lines
            const mainProduct = this.state.products.find(
                p => p.product_tmpl_id === this.env.mainProductTmplId
            );

            const otherProducts = this.state.products.filter(
                p => p.product_tmpl_id !== this.env.mainProductTmplId
            );

            const newSaleOrderLines = this.state.products.filter(
                p => p.id && !p.sale_order_line_id
            );

            const existingSaleOrderLines = this.state.products.filter(
                p => p.sale_order_line_id
            );
            // Combine both existing and new sale order lines
            const allSaleOrderLines = [
                ...existingSaleOrderLines,
                ...newSaleOrderLines
            ];

            // Deduplicate the sale order lines based on product ID
            const uniqueSaleOrderLines = Array.from(new Set(allSaleOrderLines.map(product => product.id))).map(id => allSaleOrderLines.find(product => product.id === id));

            // If there are more than 1 sale order lines, remove the extras
            if (uniqueSaleOrderLines.length > 1) {
                // Remove all but one sale order line
                uniqueSaleOrderLines.splice(1); // Keep only the first line
            }

            // Save the sale order with the main product and the unique sale order line(s)
            if (otherProducts.length) {
                for (const product of [mainProduct,...otherProducts]) {
                     if($(document.querySelectorAll('[pv_id="'+product.id+'"]')).length){
                        product.price = parseFloat(document.querySelectorAll('[pv_id="'+product.id+'"]')[0].value)
                     }
                }
                await this.props.save('mainObject',[mainProduct,...otherProducts]);
                for (const product of [mainProduct,...otherProducts]) {
                    await this.env.services.notification.add(
                        _t('Successfully Added %(qty)s Quantity %(product_name)s to Sale order.', { product_name: product.display_name,qty:product.quantity }),
                        { type: "success" }
                    );
                }
            }else{
                if($(document.querySelectorAll('[pv_id="'+mainProduct.id+'"]')).length){
                    mainProduct.price = parseFloat(document.querySelectorAll('[pv_id="'+mainProduct.id+'"]')[0].value)
                }
                await this.props.save('mainObject',[mainProduct]);
                await this.env.services.notification.add(
                    _t('Successfully Added %(qty)s Quantity %(product_name)s to Sale order.', { product_name: mainProduct.display_name,qty:mainProduct.quantity }),
                    { type: "success" }
                );
            }
        } catch (error) {
            await this.env.services.notification.add(
                _t('%(err)s', { err: error }),
                { type: "danger" }
            );
        } finally {
            this.isProcessing = false;
    //        if (!this.props.edit && this.isCustomButton == true) {
    //            this.props.discard(); // clear the line
    //        }
        }
    },
    onDiscard() {
//        if (!this.props.edit) {
//            this.props.discard(); // clear the line
//        }
        console.log("------close-----")
        this.props.close();
    },
    async _setUserPrice(productTmplId, userProductPrice,targetEl) {
       const product = this._findProduct(productTmplId);
       if(!Number.isNaN(userProductPrice)){
           if($(targetEl).length){
                targetEl.setAttribute('pv_id',product.id);
           }
       }else{
            if($(targetEl).length && targetEl.hasAttribute('pv_id')){
                targetEl.removeAttribute('pv_id');
           }
    }

    },




});
