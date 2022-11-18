odoo.define('podiatry_manager.PSNumpadInputButton', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class PSNumpadInputButton extends PosComponent {
        get _class() {
            return this.props.changeClassTo || 'input-button number-char';
        }
    }
    PSNumpadInputButton.template = 'PSNumpadInputButton';

    Registries.Component.add(PSNumpadInputButton);

    return PSNumpadInputButton;
});
