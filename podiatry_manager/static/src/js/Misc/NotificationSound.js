odoo.define('podiatry_manager.NotificationSound', function (require) {
    'use strict';

    const { useListener } = require('web.custom_hooks');
    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class NotificationSound extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('ended', () => (this.props.sound.src = null));
        }
    }
    NotificationSound.template = 'NotificationSound';

    Registries.Component.add(NotificationSound);

    return NotificationSound;
});
