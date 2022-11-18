odoo.define('podiatry_manager.ClientLine', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class ClientLine extends PosComponent {
        get highlight() {
            return this.props.partner !== this.props.selectedClient ? '' : 'highlight';
        }
    }
    ClientLine.template = 'ClientLine';

    Registries.Component.add(ClientLine);

    return ClientLine;
});
