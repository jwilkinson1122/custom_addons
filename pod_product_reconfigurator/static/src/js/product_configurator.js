odoo.define('product_reconfiguration', function (require) {
    var field_registry = require('web.field_registry');
    var core = require('web.core');
    var _t = core._t;

    var Many2one = field_registry.get('many2one');

    var ReconfigMany2one = Many2one.extend({
        start: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            def.then(function () {
                self.reinitialize(self.value.data);
            })
        }
    });

    var ProductConfiguratorFormController = require('sale.ProductConfiguratorFormController')
    var FormController = require('web.FormController');
    var OptionalProductsModal = require('sale.OptionalProductsModal');

    var ProductReConfiguratorFormController = ProductConfiguratorFormController.include({
        _onFieldChanged: function (event) {
            FormController.prototype._onFieldChanged.apply(this, arguments)
            var self = this;
            var product_id = event.data.changes.product_template_id.id;

            // check to prevent traceback when emptying the field
            if (!product_id) {
                return;
            }

            this.$el.parents('.modal').find('.o_sale_product_configurator_add').removeClass('disabled');
            var record = this.model.get(this.handle, {raw: true})
            var product_product_id = record.data.product_id || false;
            var order_line_id = record.data.order_line_id || false;
            var order_id = record.data.order_id || false;
            this._rpc({
                route: '/product_configurator/configure',
                params: {
                    product_id: product_id,
                    pricelist_id: this.renderer.pricelistId,
                    product_product_id: product_product_id,
                    order_line_id: order_line_id,
                    order_id: order_id
                }
            }).then(function (configurator) {
                self.renderer.renderConfigurator(configurator);
            });
        },
        _handleAdd: function ($modal) {
            var self = this;
            var productSelector = [
                'input[type="hidden"][name="product_id"]',
                'input[type="radio"][name="product_id"]:checked'
            ];

            var productId = parseInt($modal.find(productSelector.join(', ')).first().val(), 10);
            var productReady = this.renderer.selectOrCreateProduct(
                $modal,
                productId,
                $modal.find('.product_template_id').val(),
                false
            );

            productReady.done(function (productId) {
                $modal.find(productSelector.join(', ')).val(productId);

                var variantValues = self
                    .renderer
                    .getSelectedVariantValues($modal.find('.js_product'));

                var productCustomVariantValues = self
                    .renderer
                    .getCustomVariantValues($modal.find('.js_product'));

                var noVariantAttributeValues = self
                    .renderer
                    .getNoVariantAttributeValues($modal.find('.js_product'));

                self.rootProduct = {
                    product_id: productId,
                    quantity: parseFloat($modal.find('input[name="add_qty"]').val() || 1),
                    variant_values: variantValues,
                    product_custom_attribute_values: productCustomVariantValues,
                    no_variant_attribute_values: noVariantAttributeValues
                };
                var order_id =  parseInt($modal.find('input[type="hidden"][name="order_id"]').val(), 10)
                var order_line_id  = parseInt($modal.find('input[type="hidden"][name="order_line_id"]').val(), 10)
                var def = $.Deferred();
                if (order_id && order_line_id) {
                    var order_params =  _.extend({
                        order_id: order_id,
                        order_line_id: order_line_id
                    }, self.rootProduct)
                    def = self._rpc({
                        route: '/product_configurator/update_order',
                        params: order_params
                    });
                } else {
                    def.resolve();
                }
                def.then(function () {
                    self.optionalProductsModal = new OptionalProductsModal($('body'), {
                        rootProduct: self.rootProduct,
                        pricelistId: self.renderer.pricelistId,
                        okButtonText: _t('Confirm'),
                        cancelButtonText: _t('Back'),
                        title: _t('Configure')
                    }).open();

                    self.optionalProductsModal.on('options_empty', null,
                        self._onModalOptionsEmpty.bind(self));

                    self.optionalProductsModal.on('update_quantity', null,
                        self._onOptionsUpdateQuantity.bind(self));

                    self.optionalProductsModal.on('confirm', null,
                        self._onModalConfirm.bind(self));
                });

            });
        },

    });

    var ProductConfiguratorFormRenderer = require('sale.ProductConfiguratorFormRenderer');
    ProductConfiguratorFormRenderer.prototype.handleCustomValues = function ($target){
        var $variantContainer;
        var $customInput = false;
        if ($target.is('input[type=radio]') && $target.is(':checked')) {
            $variantContainer = $target.closest('ul').closest('li');
            $customInput = $target;
        } else if ($target.is('select')){
            $variantContainer = $target.closest('li');
            $customInput = $target
                .find('option[value="' + $target.val() + '"]');
        }

        if ($variantContainer) {
            if ($customInput && $customInput.data('is_custom')) {
                var attributeValueId = $customInput.data('value_id');
                var attributeValueName = $customInput.data('value_name');
                var attributeCustomValue =  $customInput.data('custom-value') || false;

                if ($variantContainer.find('.variant_custom_value').length === 0
                        || $variantContainer
                              .find('.variant_custom_value')
                              .data('attribute_value_id') !== parseInt(attributeValueId)){
                    $variantContainer.find('.variant_custom_value_label').remove();
                    $variantContainer.find('.variant_custom_value').remove();

                    var $input = $('<input>', {
                        type: 'text',
                        'data-attribute_value_id': attributeValueId,
                        'data-attribute_value_name': attributeValueName,
                        class: 'variant_custom_value form-control'
                    });
                    if (attributeCustomValue) {
                        $input.val(attributeCustomValue);
                    }
                    var isRadioInput = $target.is('input[type=radio]') &&
                        $target.closest('label.css_attribute_color').length === 0;

                    if (isRadioInput) {
                        $input.addClass('custom_value_radio');
                        $target.closest('div').after($input);
                    } else {
                        var $label = $('<label>', {
                            html: attributeValueName + ': ',
                            class: 'variant_custom_value_label'
                        });
                        $variantContainer.append($label).append($input);
                    }
                }
            } else {
                $variantContainer.find('.variant_custom_value_label').remove();
                $variantContainer.find('.variant_custom_value').remove();
            }
        }
    },

    field_registry.add('reconfig_template', ReconfigMany2one);
});