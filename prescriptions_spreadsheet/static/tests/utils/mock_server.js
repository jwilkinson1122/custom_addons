/** @odoo-module */

import { registry } from "@web/core/registry";
import { mockJoinSpreadsheetSession } from "@spreadsheet_edition/../tests/utils/mock_server";

registry
    .category("mock_server")
    .add("prescriptions.prescription/get_spreadsheets_to_display", function () {
        return this.models["prescriptions.prescription"].records
            .filter((prescription) => prescription.handler === "spreadsheet")
            .map((spreadsheet) => ({
                name: spreadsheet.name,
                id: spreadsheet.id,
            }));
    })
    .add("prescriptions.prescription/join_spreadsheet_session", function (route, args) {
        const result = mockJoinSpreadsheetSession("prescriptions.prescription").call(this, route, args);
        const [id] = args.args;
        const record = this.models["prescriptions.prescription"].records.find((record) => record.id === id);
        result.is_favorited = record.is_favorited;
        result.folder_id = record.folder_id;
        return result;
    })
    .add("prescriptions.prescription/dispatch_spreadsheet_message", () => false)
    .add("prescriptions.prescription/action_open_new_spreadsheet", function (route, args) {
        const spreadsheetId = this.mockCreate("prescriptions.prescription", {
            name: "Untitled spreadsheet",
            mimetype: "application/o-spreadsheet",
            spreadsheet_data: "{}",
            handler: "spreadsheet",
        });
        return {
            type: "ir.actions.client",
            tag: "action_open_spreadsheet",
            params: {
                spreadsheet_id: spreadsheetId,
                is_new_spreadsheet: true,
            },
        };
    })
    .add("spreadsheet.template/fetch_template_data", function (route, args) {
        const [id] = args.args;
        const record = this.models["spreadsheet.template"].records.find(
            (record) => record.id === id
        );
        if (!record) {
            throw new Error(`Spreadsheet Template ${id} does not exist`);
        }
        return {
            data:
                typeof record.spreadsheet_data === "string"
                    ? JSON.parse(record.spreadsheet_data)
                    : record.spreadsheet_data,
            name: record.name,
            isReadonly: false,
        };
    })
    .add(
        "spreadsheet.template/join_spreadsheet_session",
        mockJoinSpreadsheetSession("spreadsheet.template")
    );
