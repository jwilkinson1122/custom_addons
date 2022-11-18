odoo.define('podiatry_manager.WrappedProductNameLines', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class WrappedProductNameLines extends PosComponent {
        constructor() {
            super(...arguments);
            this.line = this.props.line;
        }
    }
    WrappedProductNameLines.template = 'WrappedProductNameLines';

    Registries.Component.add(WrappedProductNameLines);

    return WrappedProductNameLines;
});
