  /** @odoo-module **/

  import { _t } from "@web/core/l10n/translation";
  import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
  import { useService } from "@web/core/utils/hooks";
  import { Component } from "@odoo/owl";
  import { usePos } from "@point_of_sale/app/store/pos_hook";
  import { ShortcutTipsPopup } from "@pod_management_master/static/pod_pos_keyboard_shortcut/app/popups/shortcut_tips_popup/shortcut_tips_popup";
  
  export class ShortcutListTips extends Component {
      static template = "pod_management_master.ShortcutListTips";
      setup() {
          this.pos = usePos();
          this.popup = useService("popup");
        }
        async onClick() {
            let { confirmed } = await  this.popup.add(ShortcutTipsPopup);
            if (confirmed) {
            } else {
                return;
            }
        }
   
  }

  ProductScreen.addControlButton({
      component: ShortcutListTips,
      condition: function () {
          return this.pos.config.pod_enable_shortcut
      },
  })
