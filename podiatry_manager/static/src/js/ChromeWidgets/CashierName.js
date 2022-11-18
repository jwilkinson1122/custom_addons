odoo.define('podiatry_manager.CashierName', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    // Previously UsernameWidget
    class CashierName extends PosComponent {
        get username() {
            const { name } = this.env.pos.get_cashier();
            return name ? name : '';
        }
        get avatar() {
            const { user_id } = this.env.pos.get_cashier();
            const id = user_id && user_id.length ? user_id[0] : -1;
            return `/web/image/res.users/${id}/avatar_128`;
        }
    }
    CashierName.template = 'CashierName';

    Registries.Component.add(CashierName);

    return CashierName;
});
