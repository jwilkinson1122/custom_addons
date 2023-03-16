odoo.define('point_of_sale.Barcode', function (require) {
    'use strict';

    const { onMounted } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');


    class Barcode extends PosComponent {
        constructor() {
            super(...arguments);
            this.code = this.props.code;
            onMounted(() => this.renderBarcode());
        }

        renderBarcode() {
            $('#barcode').JsBarcode(this.code);
        }
    }

    Barcode.template = 'Barcode';

    Registries.Component.add(Barcode);

    return Barcode;
});
