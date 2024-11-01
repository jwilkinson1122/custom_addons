/** @odoo-module **/
/**  Author       :  A & M  **/
/**  Copyright(c) :  2024-Present.  **/
/**  License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).  **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import {Dropdown} from '@web/core/dropdown/dropdown';
import {DropdownItem} from '@web/core/dropdown/dropdown_item';
class PipInstaller extends Component {
   setup() {
       super.setup(...arguments);
       this.action = useService("action");
   }
   _onClick_pip_installer() {
     this.action.doAction('package_installer.pip_installer_menu_preferences_action');
   }
}
PipInstaller.template = "pip_installer";
export const PipInstallerItems = { Component: PipInstaller};
registry.category("systray").add("PipInstaller", PipInstallerItems, { sequence: 1});
