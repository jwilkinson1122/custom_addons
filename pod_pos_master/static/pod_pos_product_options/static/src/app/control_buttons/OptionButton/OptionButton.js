  /** @odoo-module **/

  import { _t } from "@web/core/l10n/translation";
  import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
  import { useService } from "@web/core/utils/hooks";
  import { Component } from "@odoo/owl";
  import { usePos } from "@point_of_sale/app/store/pos_hook";
  import { OptionsPopup } from "@pod_pos_master/static/pod_pos_product_options/app/Popups/OptionsPopup/OptionsPopup";
  import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

  export class OptionButton extends Component {
      static template = "pod_pos_product_options.OptionButton";
      setup() {
          this.pos = usePos();
          this.popup = useService("popup");
        }
        async onClick(){
            var self = this;
            var allproducts = []
           
            allproducts = self.pos.db.get_product_by_category(0) ;
            
            var Globaloptions = $.grep(allproducts, function (product) {
                return product.pod_is_global_option;
            });
            if (Globaloptions.length > 0 ){
                let { confirmed } = await  this.popup.add(OptionsPopup, {'title' : 'Global Option','Option_products': [], 'Globaloptions': Globaloptions});
                if (confirmed) {
                } else {
                    return;
                }
                // self.showPopup('OptionsPopup', {'title' : 'Global Option','Option_products': [], 'Globaloptions': Globaloptions})
            } else{
                let { confirmed } = await  this.popup.add(ErrorPopup, {title : 'No Options',body: 'Not Found any Global Option'});
                if (confirmed) {
                } else {
                    return;
                }
                // self.showPopup('ErrorPopup', { 
                //     title: 'No Options',
                //     body: 'Not Found any Global Option'
                // })
            }
        }
   
  }

  ProductScreen.addControlButton({
      component: OptionButton,
      condition: function () {
          return this.pos.config.pod_enable_options
      },
  })
