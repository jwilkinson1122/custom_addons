odoo.define('pos_create_sales_order.SaleOrderPopup', function(require){
    
    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');

    class SaleOrderPopup extends AbstractAwaitablePopup {
        constructor() {
			super(...arguments);
        }
        get saleLink(){
            var self=this;
            return `/web#model=sale.order&id=${self.props.sale_ref[0]}`;
        }
    }
    SaleOrderPopup.template = 'SaleOrderPopup';
    Registries.Component.add(SaleOrderPopup);
   
});
