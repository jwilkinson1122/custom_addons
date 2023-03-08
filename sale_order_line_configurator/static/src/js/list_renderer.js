odoo.define("sale_order_line_configurator.list_renderer", function (require) {
    "use strict";

    var core = require("web.core");
    var _t = core._t;
    var pyUtils = require("web.py_utils");
    var ListRenderer = require("web.ListRenderer");

    ListRenderer.include({
        _onAddRecord: function (ev) {
            ev.preventDefault();

            ev.stopPropagation();
            var self = this;
            this.unselectRow().then(function () {
                var context = ev.currentTarget.dataset.context;
                var pricelistId = self._getPricelistId();
                if (context && pyUtils.py_eval(context).open_product_configurator) {
                    self._rpc({
                        model: "ir.model.data",
                        method: "xmlid_to_res_id",
                        kwargs: { xmlid: "sale_product_configurator.sale_product_configurator_view_form" },
                    }).then(function (res_id) {
                        self.do_action({
                            name: _t("Configure a product"),
                            type: "ir.actions.act_window",
                            res_model: "sale.product.configurator",
                            views: [[res_id, "form"]],
                            target: "new",
                            context: { default_pricelist_id: pricelistId },
                        }, {
                            on_close: function (products) {
                                if (products && products !== "special") {
                                    self.trigger_up("add_record", {
                                        context: self._productsToRecords(products),
                                        forceEditable: "bottom",
                                        allowWarning: true,
                                        onSuccess: function () {
                                            self.unselectRow();
                                        },
                                    });
                                }
                            },
                        }
                        );
                    });
                } else {
                    self.trigger_up("add_record", { context: context && [context] });
                }
            });
        },

        _getPricelistId: function () {
            var saleOrderForm = this.getParent() && this.getParent().getParent();
            var stateData =
                saleOrderForm && saleOrderForm.state && saleOrderForm.state.data;
            var pricelist_id =
                stateData.pricelist_id &&
                stateData.pricelist_id.data &&
                stateData.pricelist_id.data.id;

            return pricelist_id;
        },

        _productsToRecords: function (products) {
            var records = [];
            _.each(products, function (product) {
                var record = {
                    default_product_id: product.product_id,
                    default_product_uom_qty: product.quantity,
                };

                if (product.no_variant_attribute_values) {
                    var default_product_no_variant_attribute_values = [];
                    _.each(
                        product.no_variant_attribute_values,
                        function (attribute_value) {
                            default_product_no_variant_attribute_values.push([
                                4,
                                parseInt(attribute_value.value),
                            ]);
                        }
                    );
                    record.default_product_no_variant_attribute_value_ids =
                        default_product_no_variant_attribute_values;
                }

                if (product.product_custom_attribute_values) {
                    var default_custom_attribute_values = [];
                    _.each(
                        product.product_custom_attribute_values,
                        function (attribute_value) {
                            default_custom_attribute_values.push([
                                0,
                                0,
                                {
                                    attribute_value_id:
                                        attribute_value.attribute_value_id,
                                    custom_value: attribute_value.custom_value,
                                },
                            ]);
                        }
                    );
                    record.default_product_custom_attribute_value_ids =
                        default_custom_attribute_values;
                }

                records.push(record);
            });

            return records;
        },
    });
});
