odoo.define("point_of_sale.CreateOrderPopup",[], function (require) {
    "use strict";

    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const Registries = require("point_of_sale.Registries");
    const framework = require("web.framework");

    class CreateOrderPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.createOrderClicked = false;
        }

        async createDraftSaleOrder() {
            await this._createSaleOrder("draft");
        }

        async createConfirmedSaleOrder() {
            await this._createSaleOrder("confirmed");
        }

        async createDeliveredSaleOrder() {
            await this._createSaleOrder("delivered");
        }

        async createInvoicedSaleOrder() {
            await this._createSaleOrder("invoiced");
        }

        async _createSaleOrder(order_state) {
            var current_order = this.env.pos.get_order();

            framework.blockUI();

            await this.rpc({
                model: "sale.order",
                method: "create_order_from_pos",
                args: [current_order.export_as_JSON(), order_state],
            })
                .catch(function (error) {
                    throw error;
                })
                .finally(function () {
                    framework.unblockUI();
                });

            this.env.pos.removeOrder(current_order);
            this.env.pos.add_new_order();
            return await super.confirm();
        }
    }

    CreateOrderPopup.template = "CreateOrderPopup";
    Registries.Component.add(CreateOrderPopup);

    return CreateOrderPopup;
});


// import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
// import { _lt } from "@web/core/l10n/translation";
// import { useState } from "@odoo/owl";

// export class CreateOrderPopup extends AbstractAwaitablePopup {
//     static template = "pos_manufacturing.OrderSelectionPopup";
//     static defaultProps = {
//         cancelText: _lt("Cancel"),
//         title: _lt("Select"),
//         body: "",
//         list: [],
//         confirmKey: false,
//     };
//     setup() {
//         super.setup();
//         this.state = useState({ selectedId: this.props.list.find((item) => item.isSelected) });
//     }
//     selectItem(itemId) {
//         this.state.selectedId = itemId;
//         this.confirm();
//     }
//     getPayload() {
//         const selected = this.props.list.find((item) => this.state.selectedId === item.id);
//         return selected && selected.item;
//     }
// }

