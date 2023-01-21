odoo.define('pod_erp.screens', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const { useListener } = require('web.custom_hooks');
    const { debounce } = owl.utils;

    //-----------------------------------------
    //-----------------------------------------
    // Prescription History Screen
    //-----------------------------------------
    //-----------------------------------------

    class PrescriptionListScreenWidget extends IndependentToOrderScreen {
        constructor() {
            super(...arguments);

            this.updateClientList = debounce(this.updateClientList, 70);
            this.updateDateList = debounce(this.updateDateList, 70);

            this.pod_orders = this.props.all_orders;
            this.pod_order = 0;
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
                this.pod_orders = this.pod_orders.filter(function (el) { return el.customer[1].toLowerCase().includes(self.search.client.toLowerCase()) })
            else if (this.search.client == '') {
                this.pod_orders = this.props.all_orders;
                if (this.search.date != '' && this.search.date != null)
                    this.pod_orders = this.pod_orders.filter(function (el) { return el.prescription_date.toLowerCase().includes(self.search.date.toLowerCase()) })
            }
            this.render();
        }

        updateDateList(event) {
            var self = this;
            this.search.date = event.target.value;
            if (this.search.date != '')
                this.pod_orders = this.pod_orders.filter(function (el) { return el.prescription_date.toLowerCase().includes(self.search.date.toLowerCase()) })
            else if (this.search.date == '') {
                this.pod_orders = this.props.all_orders;
                if (this.search.client != '' && this.search.client != null)
                    this.pod_orders = this.pod_orders.filter(function (el) { return el.customer[1].toLowerCase().includes(self.search.client.toLowerCase()) })
            }
            this.render();
        }

        prescription_line_click(data) {
            if (this.pod_order.id == data.id)
                this.pod_order = 0;
            else
                this.pod_order = data;
            this.render();
        }

        prescription_line_button(data) {
            var self = this;
            var order = self.env.pos.get_order();
            var pod_order = self.env.pos.pod.order_by_id[parseInt(data.id)];
            $('.pod_prescription').text(data.name);
            order.set_pod_reference(data);
            order.set_client(self.env.pos.db.partner_by_id[pod_order.customer[0]]);
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