/** @odoo-module */

import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";

export class SaleOrderPopup extends Component {
    static template = "pod_pos_create_sales_order.SaleOrderPopup";
    static components = { Dialog }; 
    static props ={
        close: { type: Function },
        sale_ref : Object, 
    }

    get saleLink(){
        var self=this;
        return `/web#model=sale.order&id=${self.props.sale_ref[0]}`;
    }
}
