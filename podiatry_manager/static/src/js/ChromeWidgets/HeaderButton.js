odoo.define('podiatry_manager.HeaderButton', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    // Previously HeaderButtonWidget
    // This is the close session button
    class HeaderButton extends PosComponent {
        onClick() {
            this.showPopup('ClosePosPopup');
        }
    }
    HeaderButton.template = 'HeaderButton';

    Registries.Component.add(HeaderButton);

    return HeaderButton;
});
