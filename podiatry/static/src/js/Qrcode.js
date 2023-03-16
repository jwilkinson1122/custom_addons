odoo.define('point_of_sale.Qrcode', function (require) {
    'use strict';

    const { onMounted } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');


    class Qrcode extends PosComponent {
        constructor() {
            super(...arguments);
            this.code = this.props.code;
            onMounted(() => this.renderQrcode());
        }

        renderQrcode() {
            try {
                new QRCode('qr', {
                    text: this.code,
                    width: 128,
                    height: 128,
                    colorDark: "#000000",
                    colorLight: "#ffffff",
                    correctLevel: QRCode.CorrectLevel.H
                });
            } catch (e) {
            }

        }
    }

    Qrcode.template = 'Qrcode';

    Registries.Component.add(Qrcode);

    return Qrcode;
});
