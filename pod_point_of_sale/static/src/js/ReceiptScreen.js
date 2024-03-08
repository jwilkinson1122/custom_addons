odoo.define('pod_point_of_sale.main',[], function (require) {
    "use strict";

    const {useRef, onMounted} = owl.hooks;

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');


    const PosReceiptScreenExt = ReceiptScreen =>
        class extends ReceiptScreen {
            constructor() {
                super(...arguments);
                this.btnPrintA4 = useRef('btn-print-a4');
                this.posReceiptContainer = useRef('pos-receipt-container');
                onMounted(() => this.setA4ButtonVisibility());

            }

            setA4ButtonVisibility() {
                if (!this.env.pos.config.a4_receipt || this.env.pos.config.a4_receipt_as_default) {
                    this.btnPrintA4.el.style.display = 'none';
                }
            }

            async printA4Receipt(ev) {
                const order = this.currentOrder;
                const $currentTarget = $(ev.currentTarget);
                $currentTarget.toggleClass("highlight");
                let mountComponent = $currentTarget.hasClass("highlight") ? 'OrderReceiptA4' : 'OrderReceipt';
                const orderReceipt = new (Registries.Component.get(mountComponent))(this, {order});

                let receiptToRemove = this.posReceiptContainer.el ? this.posReceiptContainer.el.querySelectorAll('.pos-receipt') : [];
                receiptToRemove.forEach(el => el.parentNode.removeChild(el));

                await orderReceipt.mount(this.posReceiptContainer.el);
            }
        };

    Registries.Component.extend(ReceiptScreen, PosReceiptScreenExt);

    return ReceiptScreen;

});
