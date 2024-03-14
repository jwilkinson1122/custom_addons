odoo.define('pos_create_sales_order.SaleCreatePopup', function(require){
    
    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');

    class SaleCreatePopup extends AbstractAwaitablePopup {
        constructor() {
			super(...arguments);
            
        }
        create_order(){
            var self = this;
			var order = self.env.pos.get_order();
			var session_id = order.pos.pos_session.id;
			var orderlines = order.orderlines;
			var cashier_id = self.env.pos.get_cashier().user_id[0];
			var partner_id = false;
			var pos_product_list = [];
            var terms = $.trim($("#terms").val());
            var ord_state = $('#ord_state').val()


            if (order.get_client() != null)
				partner_id = order.get_client().id;
			
			if (!partner_id) {
				return self.showPopup('ErrorPopup', {
					title: self.env._t('Unknown customer'),
					body: self.env._t('You cannot Create Sales Order. Select customer first.'),
				});
			}

			if (orderlines.length === 0) {
				return self.showPopup('ErrorPopup', {
					title: self.env._t('Empty Order'),
					body: self.env._t('There must be at least one product in your order.'),
				});
			}
			
			for (var i = 0; i < orderlines.length; i++) {
				var product_items = {
					'id': orderlines.models[i].product.id,
					'quantity': orderlines.models[i].quantity,
					'uom_id': orderlines.models[i].product.uom_id[0],
					'price': orderlines.models[i].price,
					'discount': orderlines.models[i].discount,
				};
				pos_product_list.push({'product': product_items });
			}
			
			self.rpc({
				model: 'pos.create.sales.order',
				method: 'create_sales_order',
				args: [partner_id, partner_id, pos_product_list, cashier_id,terms,ord_state,session_id],
			}).then(function(output) {
                order.destroy({ reason: 'abandon' });
                posbus.trigger('order-deleted');
                self.env.pos.trigger('change:selectedOrder', self.env.pos, self.env.pos.get_order());
				self.cancel();
				self.showPopup('SaleOrderPopup',{'sale_ref': output,})
                
			});

        }

    }
    SaleCreatePopup.template = 'SaleCreatePopup';
    Registries.Component.add(SaleCreatePopup);
   
});
