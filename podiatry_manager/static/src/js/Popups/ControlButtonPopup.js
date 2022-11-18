odoo.define('podiatry_manager.ControlButtonPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('podiatry_manager.AbstractAwaitablePopup');
    const Registries = require('podiatry_manager.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    class ControlButtonPopup extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
            this.controlButtons = this.props.controlButtons;
        }
    }
    ControlButtonPopup.template = 'ControlButtonPopup';
    ControlButtonPopup.defaultProps = {
        cancelText: _lt('Back'),
        controlButtons: []
    };

    Registries.Component.add(ControlButtonPopup);

    return ControlButtonPopup;
});
