/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ViewPrescriptionOrderButton extends Component {
    static template = "pod_create_rx_from_pos.ViewPrescriptionOrderButton";
    setup() {
        this.pos = usePos();
    }
    async onClick() {
        var self = this;
        this.pos.showScreen('PrescriptionOrderScreen');
    }
}

ProductScreen.addControlButton({
    component: ViewPrescriptionOrderButton,
    condition: function () {
        return this.pos.config.create_rx;
    },
});


// odoo.define('pod_create_rx_from_pos.ViewPrescriptionOrderButton', function(require) {
//     'use strict';

//     const PosComponent = require('point_of_sale.PosComponent');
//     const ProductScreen = require('point_of_sale.ProductScreen');
//     const { useListener } = require("@web/core/utils/hooks");
//     const Registries = require('point_of_sale.Registries');


//     class ViewPrescriptionOrderButton extends PosComponent {
//         setup() {
//             super.setup();
//             useListener('click', this.onClick);
//         }
//         async onClick() {
//             var self = this;
//             this.showScreen('PrescriptionOrderScreen');
//         }
//     }
//     ViewPrescriptionOrderButton.template = 'ViewPrescriptionOrderButton';

//     ProductScreen.addControlButton({
//         component: ViewPrescriptionOrderButton,
//         condition: function() {
//             return this.env.pos.config.create_rx;
//         },
//     });

//     Registries.Component.add(ViewPrescriptionOrderButton);

//     return ViewPrescriptionOrderButton;
// });
