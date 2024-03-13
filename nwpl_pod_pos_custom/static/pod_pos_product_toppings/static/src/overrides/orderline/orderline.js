/** @odoo-module */

import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.pos = usePos();
        this.popup = useService("popup");
    },
    async _clickRemoveLine(line_id) {
        var self = this;
        event.stopPropagation()
        
        setTimeout(async () => {
            var order = self.pos.get_order()
            var line = self.pos.get_order().get_orderline(line_id)
            if (order && order.get_selected_orderline() && order.get_selected_orderline().Options) {
                
                var data = await $.grep(order.get_selected_orderline().Options, function (option) {
                    return option.id != line_id;
                });

                var data1 = await $.grep(order.get_selected_orderline().Options_temp, function (option1) {
                    return option1.id != line_id;
                });
                
                order.get_selected_orderline().Options = data
                order.get_selected_orderline().Options_temp = data1

                self.pos.get_order().removeOrderline(line)
            }
        }, 100);
    },
    
});
