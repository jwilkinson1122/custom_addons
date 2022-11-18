odoo.define('podiatry_manager.Notification', function (require) {
    'use strict';

    const { useListener } = require('web.custom_hooks');
    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class Notification extends PosComponent {
        constructor() {
            super(...arguments)
            useListener('click', this.closeNotification);
        }
        mounted() {
            setTimeout(() => {
                this.closeNotification();
            }, this.props.duration)
        }
    }
    Notification.template = 'Notification';

    Registries.Component.add(Notification);

    return Notification;
});
