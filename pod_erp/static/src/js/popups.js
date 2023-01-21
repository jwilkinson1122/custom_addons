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
            this.env.pos.pod.ProductCreationScreen = undefined;
            this.doctors = this.env.pos.pod.doctors;
            this.partners = this.env.pos.db.get_partners_sorted();
            this.device_type = this.env.pos.pod.device_type;
            if (this.env.pos.get_order().attributes.client)
                this.customer = this.env.pos.get_order().attributes.client.id;
            else
                this.customer = false;
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
            vals["dr"] = $('option:selected', $('[name=dr]')).data('id');
            vals["customer"] = $('option:selected', $('[name=customer]')).data('id');
            vals["device_type"] = $('option:selected', $('[name=device_type]')).data('id');
            vals = JSON.stringify(vals);
            var prescription_date = $('[name=prescription_date]').val();
            var today = new Date().toJSON().slice(0, 10);
            if (!prescription_date) {
                //                this.env.pos.pod.ProductCreationScreen = this.gui.current_popup;
                //                this.env.pos.pod.ProductCreationScreen.hide();
                //                this.gui.current_popup = this.gui.popup_instances['error'];
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Prescription date is empty'),
                    body: this.env._t('You need to select a Prescription date'),
                });
                //                    cancel: function () {
                //                        this.env.pos.pod.ProductCreationScreen.$el.removeClass('oe_hidden');
                //                        this.gui.current_popup = this.env.pos.pod.ProductCreationScreen
                //                        this.env.pos.pod.ProductCreationScreen = undefined;
                //                    }
                //                });
            }
            else {
                const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Create a Prescription ?'),
                    body: this.env._t('Are You Sure You Want a Create a Prescription'),
                });
                if (confirmed) {
                    this.env.pos.pod.ProductCreationScreen = undefined;
                    rpc.query({
                        model: 'dr.prescription',
                        method: 'create_product_pos',
                        args: [vals],
                    }).then(function (products) {
                        self.env.pos.pod.all_orders.push(products);
                        self.env.pos.pod.order_by_id[products.id] = products;
                        $('.pod_prescription').text(products.name);
                        order.set_pod_reference(products);
                        order.set_client(self.env.pos.db.partner_by_id[products.customer[0]]);
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
            this.variants1 = self.env.pos.pod.variants1;
            this.variants2 = self.env.pos.pod.variants2;
            this.variants3 = self.env.pos.pod.variants3;
            this.variants4 = self.env.pos.pod.variants4;
            this.customer = this.env.pos.get_order().attributes.client.name;
            this.pod_reference = this.env.pos.get_order().pod_reference.name;
        }
        mounted() {
        }
        render_list() {
        }
        attribute_variant_onChange() {
            var vals = $("#order_form").serializeObject();
            var variants = []
            $('#glasses').html("");
            this.env.pos.pod.glasses.forEach(function (pod_glass) {
                pod_glass.attribute_line_ids.forEach(function (attribute_line_id) {
                    variants.push(self.env.pos.pod.product_attributes_lines_by_id[attribute_line_id].display_name);
                })
                pod_glass.product_variant_ids.forEach(function (product_template) {
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