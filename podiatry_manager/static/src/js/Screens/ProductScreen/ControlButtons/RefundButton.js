odoo.define('podiatry_manager.RefundButton', function (require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const ProductScreen = require('podiatry_manager.ProductScreen');
    const Registries = require('podiatry_manager.Registries');
    const { useListener } = require('web.custom_hooks');

    class RefundButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this._onClick);
        }
        _onClick() {
            const customer = this.env.pos.get_order().get_client();
            const searchDetails = customer ? { fieldName: 'CUSTOMER', searchTerm: customer.name } : {};
            this.trigger('close-popup');
            this.showScreen('TicketScreen', {
                ui: { filter: 'SYNCED', searchDetails },
                destinationOrder: this.env.pos.get_order(),
            });
        }
    }
    RefundButton.template = 'podiatry_manager.RefundButton';

    ProductScreen.addControlButton({
        component: RefundButton,
        condition: function () {
            return true;
        },
    });

    Registries.Component.add(RefundButton);

    return RefundButton;
});
