odoo.define('pod_erp.screens', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const { useListener } = require('web.custom_hooks');
    const { debounce } = owl.utils;

    //-----------------------------------------
    //-----------------------------------------
    // Prescription Screen
    //-----------------------------------------
    //-----------------------------------------

    class PrescriptionListScreenWidget extends IndependentToOrderScreen {
        constructor() {
            super(...arguments);

            this.updateClientList = debounce(this.updateClientList, 70);
            this.updateDateList = debounce(this.updateDateList, 70);

            this.podiatry_orders = this.props.all_orders;
            this.podiatry_order = 0;
            this.selected_line = null;
            this.search = {
                date: null,
                client: null,
            };
        }

        updateClientList(event) {
            var self = this;
            this.search.client = event.target.value;
            if (this.search.client != '')
                this.podiatry_orders = this.podiatry_orders.filter(function (el) { return el.patient[1].toLowerCase().includes(self.search.client.toLowerCase()) })
            else if (this.search.client == '') {
                this.podiatry_orders = this.props.all_orders;
                if (this.search.date != '' && this.search.date != null)
                    this.podiatry_orders = this.podiatry_orders.filter(function (el) { return el.prescription_date.toLowerCase().includes(self.search.date.toLowerCase()) })
            }
            this.render();
        }

        updateDateList(event) {
            var self = this;
            this.search.date = event.target.value;
            if (this.search.date != '')
                this.podiatry_orders = this.podiatry_orders.filter(function (el) { return el.prescription_date.toLowerCase().includes(self.search.date.toLowerCase()) })
            else if (this.search.date == '') {
                this.podiatry_orders = this.props.all_orders;
                if (this.search.client != '' && this.search.client != null)
                    this.podiatry_orders = this.podiatry_orders.filter(function (el) { return el.patient[1].toLowerCase().includes(self.search.client.toLowerCase()) })
            }
            this.render();
        }

        prescription_line_click(data) {
            if (this.podiatry_order.id == data.id)
                this.podiatry_order = 0;
            else
                this.podiatry_order = data;
            this.render();
        }

        prescription_line_button(data) {
            var self = this;
            var order = self.env.pos.get_order();
            var podiatry_order = self.env.pos.podiatry.order_by_id[parseInt(data.id)];
            $('.podiatry_prescription').text(data.name);
            order.set_podiatry_reference(data);
            order.set_client(self.env.pos.db.partner_by_id[podiatry_order.patient[0]]);
            this.close();

        }

        print_receipt(data) {
            this.close();
            this.showScreen('PrescriptionPrint', { prescription: data.id });
        }

        mounted() {
            this.render();
        }

        back() {
            this.close();
        }

    }

    PrescriptionListScreenWidget.template = 'PrescriptionHistoryScreenContainer';
    Registries.Component.add(PrescriptionListScreenWidget);

    return PrescriptionListScreenWidget;

});