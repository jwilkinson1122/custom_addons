odoo.define('optical_erp.PrescriptionPrint', function (require) {
    'use strict';

    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const { useRef } = owl.hooks;

    const PrescriptionPrint = (AbstractReceiptScreen) => {
        class PrescriptionPrint extends AbstractReceiptScreen {

        constructor() {
            super(...arguments);
            this.company = this.env.pos.company;
            this.company.logo =  this.env.pos.company_logo_base64;
            this.cashier = this.env.pos.get_cashier();
            this.date    = new Date().toString().slice(0,-34);
            this.optical_order = this.env.pos.optical.order_by_id[this.props.prescription];
        }

        back() {
            this.showScreen('ProductScreen');
        }
    }

    PrescriptionPrint.template = 'PrintPrescriptionScreenWidget';
    return PrescriptionPrint
    };

    Registries.Component.addByExtending(PrescriptionPrint, AbstractReceiptScreen);


    return PrescriptionPrint;
});
