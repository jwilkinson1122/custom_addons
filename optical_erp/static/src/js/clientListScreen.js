odoo.define('optical_erp.ClientListScreen', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const ClientListScreen = require('point_of_sale.ClientListScreen');

    const optical_erp_ClientListScreen = ClientListScreen =>
    class extends ClientListScreen {

        get prescription_count(){
            self = this;
            if (this.state.selectedClient)
                return self.env.pos.optical.all_orders.filter(function(el){return el.customer[0] === self.state.selectedClient.id}).length
            else
                return 0
        }

        prescription_count_click(data){
            var optical_orders = this.env.pos.optical.all_orders.filter(function(el){return el.customer[0] === data.id})
            this.trigger('close-temp-screen');
            this.showScreen('PrescriptionListScreenWidget',{all_orders:optical_orders});
        }

    }
    Registries.Component.extend(ClientListScreen,optical_erp_ClientListScreen);
});