/** @odoo-module */

import { AbstractAwaitablePopup } from "@pod_point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";

export class ConfirmPopup extends AbstractAwaitablePopup {
    static template = "pod_point_of_sale.ConfirmPopup";
    static defaultProps = {
        confirmText: _t("Ok"),
        cancelText: _t("Cancel"),
        title: _t("Confirm?"),
        body: "",
    };
}
