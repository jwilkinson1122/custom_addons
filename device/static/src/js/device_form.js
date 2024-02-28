/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";

export class DeviceFormController extends FormController {
    /**
     * @override
     **/
    getStaticActionMenuItems() {
        const menuItems = super.getStaticActionMenuItems();
        menuItems.archive.callback = () => {
            const dialogProps = {
                body: _t(
                    "Every service and contract of this custom will be considered as archived. Are you sure that you want to archive this record?"
                ),
                confirm: () => this.model.root.archive(),
                cancel: () => {},
            };
            this.dialogService.add(ConfirmationDialog, dialogProps);
        };
        return menuItems;
    }
}

export const deviceFormView = {
    ...formView,
    Controller: DeviceFormController,
};

registry.category("views").add("device_form", deviceFormView);
