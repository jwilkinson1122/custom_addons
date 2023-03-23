odoo.define('pod_erp.popups', function (require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');
    var rpc = require('web.rpc');

    //-----------------------------------------
    //-----------------------------------------
    // Prescription Popup
    //-----------------------------------------
    //-----------------------------------------

    class PrescriptionCreationWidget extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.env.pos.podiatry.ProductCreationScreen = undefined;
            this.practitioners = this.env.pos.podiatry.practitioners;
            this.partners = this.env.pos.db.get_partners_sorted();
            this.test_type = this.env.pos.podiatry.test_type;
            this.device_type = this.env.pos.podiatry.device_type;
            if (this.env.pos.get_order().attributes.client)
                this.patient = this.env.pos.get_order().attributes.client.id;
            else
                this.patient = false;
            var abc = [];
            for (var i = 0; i < 180; i++)
                abc.push(i);
            this.abc = abc;
            this.today = new Date().toISOString().substr(0, 10);;
        }
        mounted() {
        }
        render_list() {
        }
        async click_confirm() {
            var self = this;
            var order = this.env.pos.get_order();
            var vals = $("#prescription_form").serializeObject();
            vals["practitioner"] = $('option:selected', $('[name=practitioner]')).data('id');
            vals["patient"] = $('option:selected', $('[name=patient]')).data('id');
            vals["test_type"] = $('option:selected', $('[name=test_type]')).data('id');
            vals["device_type"] = $('option:selected', $('[name=device_type]')).data('id');
            vals = JSON.stringify(vals);
            var prescription_date = $('[name=prescription_date]').val();
            var today = new Date().toJSON().slice(0, 10);
            if (!prescription_date) {
                //                this.env.pos.podiatry.ProductCreationScreen = this.gui.current_popup;
                //                this.env.pos.podiatry.ProductCreationScreen.hide();
                //                this.gui.current_popup = this.gui.popup_instances['error'];
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Prescription date is empty'),
                    body: this.env._t('You need to select a Prescription date'),
                });
                //                    cancel: function () {
                //                        this.env.pos.podiatry.ProductCreationScreen.$el.removeClass('oe_hidden');
                //                        this.gui.current_popup = this.env.pos.podiatry.ProductCreationScreen
                //                        this.env.pos.podiatry.ProductCreationScreen = undefined;
                //                    }
                //                });
            }
            else {
                const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Create a Prescription ?'),
                    body: this.env._t('Are You Sure You Want a Create a Prescription'),
                });
                if (confirmed) {
                    this.env.pos.podiatry.ProductCreationScreen = undefined;
                    rpc.query({
                        model: 'practitioner.prescription',
                        method: 'create_product_pos',
                        args: [vals],
                    }).then(function (products) {
                        self.env.pos.podiatry.all_orders.push(products);
                        self.env.pos.podiatry.order_by_id[products.id] = products;
                        $('.podiatry_prescription').text(products.name);
                        order.set_podiatry_reference(products);
                        order.set_client(self.env.pos.db.partner_by_id[products.patient[0]]);
                    });
                }
            };
        }
        cancel() {
            this.trigger('close-popup');
        }

    }
    PrescriptionCreationWidget.template = 'PrescriptionCreationWidget';
    Registries.Component.add(PrescriptionCreationWidget);

    //-----------------------------------------
    //-----------------------------------------
    // OrderCreationWidget Popup
    //-----------------------------------------
    //-----------------------------------------

    class OrderCreationWidget extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            self = this;
            this.variants1 = self.env.pos.podiatry.variants1;
            this.variants2 = self.env.pos.podiatry.variants2;
            this.variants3 = self.env.pos.podiatry.variants3;
            this.variants4 = self.env.pos.podiatry.variants4;
            this.patient = this.env.pos.get_order().attributes.client.name;
            this.podiatry_reference = this.env.pos.get_order().podiatry_reference.name;
        }
        mounted() {
        }
        render_list() {
        }
        attribute_variant_onChange() {
            var vals = $("#order_form").serializeObject();
            var variants = []
            $('#glasses').html("");
            this.env.pos.podiatry.glasses.forEach(function (podiatry_glass) {
                podiatry_glass.attribute_line_ids.forEach(function (attribute_line_id) {
                    variants.push(self.env.pos.podiatry.product_attributes_lines_by_id[attribute_line_id].display_name);
                })
                podiatry_glass.product_variant_ids.forEach(function (product_template) {
                    if (variants.every(function (variant) { return self.env.pos.db.product_by_id[product_template].display_name.includes(vals[variant]) })) {
                        $('#glasses').append($('<option>', {
                            value: product_template,
                            text: self.env.pos.db.product_by_id[product_template].display_name
                        }));
                    }
                })
                variants = [];
            })
        }
        click_confirm() {
            var order = this.env.pos.get_order();
            var id = $('option:selected', $('#glasses')).val();
            var found = false;
            if (id !== undefined)
                order.add_product(this.env.pos.db.product_by_id[id]);
            self.trigger('close-popup');
        }
        cancel() {
            self.trigger('close-popup');
        }
    }
    OrderCreationWidget.template = 'OrderCreationWidget';
    Registries.Component.add(OrderCreationWidget);

    return PrescriptionCreationWidget, OrderCreationWidget;
});