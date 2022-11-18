odoo.define('podiatry_manager.OrderDetails', function (require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    /**
     * @props {models.Order} order
     */
    class OrderDetails extends PosComponent {
        get order() {
            return this.props.order;
        }
        get orderlines() {
            return this.order ? this.order.orderlines.models : [];
        }
        get total() {
            return this.env.pos.format_currency(this.order ? this.order.get_total_with_tax() : 0);
        }
        get tax() {
            return this.env.pos.format_currency(this.order ? this.order.get_total_tax() : 0)
        }
    }
    OrderDetails.template = 'OrderDetails';

    Registries.Component.add(OrderDetails);

    return OrderDetails;
});
