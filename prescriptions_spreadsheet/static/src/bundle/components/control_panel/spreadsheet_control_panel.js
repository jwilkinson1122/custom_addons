/** @odoo-module **/

import { SpreadsheetControlPanel } from "@spreadsheet_edition/bundle/actions/control_panel/spreadsheet_control_panel";

export class PrescriptionsSpreadsheetControlPanel extends SpreadsheetControlPanel {}

PrescriptionsSpreadsheetControlPanel.template =
    "prescriptions_spreadsheet.PrescriptionsSpreadsheetControlPanel";
PrescriptionsSpreadsheetControlPanel.components = {
    ...SpreadsheetControlPanel.components,
};
PrescriptionsSpreadsheetControlPanel.props = {
    ...SpreadsheetControlPanel.props,
    isFavorited: {
        type: Boolean,
        optional: true,
    },
    onFavoriteToggled: {
        type: Function,
        optional: true,
    },
    onSpreadsheetShared: {
        type: Function,
        optional: true,
    },
};
