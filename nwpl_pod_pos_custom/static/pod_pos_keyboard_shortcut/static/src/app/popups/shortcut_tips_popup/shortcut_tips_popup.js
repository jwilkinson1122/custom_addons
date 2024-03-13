/** @odoo-module */
    
    
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
   
export class ShortcutTipsPopup extends AbstractAwaitablePopup {
    static template = "nwpl_pod_pos_custom.ShortcutTipsPopup";
        setup() {
            super.setup();
            this.pos = usePos();
        } 
    }
