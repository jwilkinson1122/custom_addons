odoo.define('pos_multi_variant.ProductScreen', function (require) {
    'use strict';

    var ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var gui = require("point_of_sale.gui");
    var core = require("web.core");
    var framework = require("web.framework");
    var rpc = require("web.rpc");
    var _t = core._t;

    models.load_models([
        {
            model: 'variants.tree',
            fields: ["pos_active", "value", "attribute", "variants_id", "extra_price"],
            loaded: function (self, variants_tree) {
                self.variant_tree = variants_tree;
                _.each(variants_tree, function (item) {
                    self.item = item;
                });
            }
        }, {
            model: 'product.attribute.value',
            fields: ["id", "name"],
            loaded: function (self, values) {
                self.values = values;
            }
        }]);

    var super_models = models.PosModel.prototype.models;
    models.load_fields('product.product', 'pos_variants');
    models.load_fields('product.product', 'variant_line_ids');

    /** **********************************************************************
        New Widget CreateSaleOrderButtonWidget:
            * On click, display a new screen to select the action to do
    */
    var CreateSaleOrderButtonWidget = ProductScreen.ActionButtonWidget.extend({
        template: "CreateSaleOrderButtonWidget",

        button_click: function () {
            if (this.pos.get_order().get_client()) {
                this.gui.show_screen("create_sale_order");
            } else {
                this.gui.show_popup("error", {
                    title: _t("No customer defined"),
                    body: _t(
                        "You should select a customer in order to create" +
                        " a Sale Order."
                    ),
                });
            }
        },

        is_visible: function () {
            return this.pos.get_order().orderlines.length > 0;
        },
    });

    ProductScreen.define_action_button({
        name: "create_sale_order",
        widget: CreateSaleOrderButtonWidget,
        condition: function () {
            return this.pos.config.iface_create_sale_order;
        },
    });

    ProductScreen.OrderWidget.include({
        update_summary: function () {
            this._super();
            if (
                this.getParent().action_buttons &&
                this.getParent().action_buttons.create_sale_order
            ) {
                this.getParent().action_buttons.create_sale_order.renderElement();
            }
        },
    });

    /** **********************************************************************
        New ScreenWidget CreateSaleOrderScreenWidget:
            * On show, display all buttons, depending on the pos configuration
    */
    var CreateSaleOrderScreenWidget = screens.ScreenWidget.extend({
        template: "CreateSaleOrderScreenWidget",
        auto_back: true,

        show: function () {
            var self = this;
            this._super();

            this.renderElement();

            this.$(".back").click(function () {
                self.gui.back();
            });

            if (!this.pos.config.iface_create_draft_sale_order) {
                this.$("#button-create-draft-order").addClass("oe_hidden");
            }
            if (!this.pos.config.iface_create_confirmed_sale_order) {
                this.$("#button-create-confirmed-order").addClass("oe_hidden");
            }
            if (!this.pos.config.iface_create_delivered_sale_order) {
                this.$("#button-create-delivered-order").addClass("oe_hidden");
            }

            this.$(".paymentmethod").click(function (event) {
                self.click_sale_order_button(
                    event.currentTarget.attributes.action.nodeValue
                );
            });
        },

        click_sale_order_button: function (action) {
            var self = this;
            this.gui.show_popup("confirm", {
                title: _t("Create Sale Order and discard the current" + " PoS Order?"),
                body: _t(
                    "This operation will permanently discard the current PoS" +
                    " Order and create a Sale Order, based on the" +
                    " current order lines."
                ),
                confirm: function () {
                    framework.blockUI();
                    rpc.query({
                        model: "sale.order",
                        method: "create_order_from_pos",
                        args: [self.pos.get("selectedOrder").export_as_JSON(), action],
                    })
                        .then(function () {
                            self.hook_create_sale_order_success();
                        })
                        .catch(function (error, event) {
                            self.hook_create_sale_order_error(error, event);
                        });
                },
            });
        },

        /**
         * Overloadable function to make custom action after Sale order
         * Creation succeeded
         */
        hook_create_sale_order_success: function () {
            framework.unblockUI();
            this.pos.get("selectedOrder").destroy();
        },

        /**
         * Overloadable function to make custom action after Sale order
         * Creation failed
         */
        hook_create_sale_order_error: function (error, event) {
            framework.unblockUI();
            event.preventDefault();
            if (error.code === 200) {
                // Business Logic Error, not a connection problem
                this.gui.show_popup("error-traceback", {
                    title: error.data.message,
                    body: error.data.debug,
                });
            } else {
                // Connexion problem
                this.gui.show_popup("error", {
                    title: _t("The order could not be sent"),
                    body: _t("Check your internet connection and try again."),
                });
            }
        },
    });

    gui.define_screen({
        name: "create_sale_order",
        widget: CreateSaleOrderScreenWidget,
        condition: function () {
            return this.pos.config.iface_create_sale_order;
        },
    });

    return {
        CreateSaleOrderButtonWidget: CreateSaleOrderButtonWidget,
        CreateSaleOrderScreenWidget: CreateSaleOrderScreenWidget,
    };

    const ProductScreenExtend = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
            }

            async _clickProduct(event) {
                if (!this.currentOrder) {
                    this.env.pos.add_new_order();
                }
                const product = event.detail;
                var variant_product = ''
                await rpc.query({
                    model: 'variants.tree',
                    method: 'search_read',
                    fields: ['extra_price', 'attribute', 'value', 'variants_id'],
                    args: [[['variants_id', '=', event.detail.product_tmpl_id]]]
                }).then(function (data) {
                    variant_product = data

                });
                var li = []
                for (var i = 0; i < variant_product.length; ++i) {
                    variant_product[i].value.forEach(function (field) {
                        li.push(field)
                    });

                }

                var variant_details = ''
                await rpc.query({
                    model: 'product.attribute.value',
                    method: 'search_read',
                    fields: ['name'],
                    domain: [['id', 'in', li]],
                }).then(function (result) {
                    variant_details = result
                });

                const options = await this._getAddProductOptions(product);

                // Do not add product if options is undefined.
                if (!options) return;
                // Add the product after having the extra information.
                this.currentOrder.add_product(product, options);
                NumberBuffer.reset();
                if (product.pos_variants)
                    this.showPopup('ProductsPopup', {
                        title: product.display_name,
                        products: variant_product,
                        product_tmpl_id: event.detail.id,
                        variant_details: variant_details,
                    });
            }


        };

    Registries.Component.extend(ProductScreen, ProductScreenExtend);
    return ProductScreen;



});