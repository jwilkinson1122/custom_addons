odoo.define('podiatry_manager.TicketButton', function (require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');
    const { posbus } = require('podiatry_manager.utils');

    class TicketButton extends PosComponent {
        onClick() {
            if (this.props.isTicketScreenShown) {
                posbus.trigger('ticket-button-clicked');
            } else {
                this.showScreen('TicketScreen');
            }
        }
        willPatch() {
            posbus.off('order-deleted', this);
        }
        patched() {
            posbus.on('order-deleted', this, this.render);
        }
        mounted() {
            posbus.on('order-deleted', this, this.render);
        }
        willUnmount() {
            posbus.off('order-deleted', this);
        }
        get count() {
            if (this.env.pos) {
                return this.env.pos.get_order_list().length;
            } else {
                return 0;
            }
        }
    }
    TicketButton.template = 'TicketButton';

    Registries.Component.add(TicketButton);

    return TicketButton;
});
