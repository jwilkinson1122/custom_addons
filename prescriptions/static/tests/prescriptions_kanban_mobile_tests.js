/* @odoo-module */

import { startServer } from "@bus/../tests/helpers/mock_python_environment";

import { createPrescriptionsViewWithMessaging } from "./prescriptions_test_utils";
import { prescriptionService } from "@prescriptions/core/prescription_service";
import { storeService } from "@mail/core/common/store_service";
import { attachmentService } from "@mail/core/common/attachment_service";
import { voiceMessageService } from "@mail/discuss/voice_message/common/voice_message_service";
import { multiTabService } from "@bus/multi_tab_service";
import { busParametersService } from "@bus/bus_parameters_service";
import { busService } from "@bus/services/bus_service";

import { registry } from "@web/core/registry";
import { click, getFixture, nextTick, patchWithCleanup } from "@web/../tests/helpers/utils";
import { setupViewRegistries } from "@web/../tests/views/helpers";
import { fileUploadService } from "@web/core/file_upload/file_upload_service";
import { PrescriptionsListRenderer } from "@prescriptions/views/list/prescriptions_list_renderer";

const serviceRegistry = registry.category("services");

let target;

QUnit.module("prescriptions", {}, function () {
    QUnit.module(
        "prescriptions_kanban_mobile_tests.js",
        {
            async beforeEach() {
                setupViewRegistries();
                target = getFixture();
                const REQUIRED_SERVICES = {
                    prescriptions_pdf_thumbnail: {
                        start() {
                            return {
                                enqueueRecords: () => {},
                            };
                        },
                    },
                    "prescription.prescription": prescriptionService,
                    "mail.attachment": attachmentService,
                    "mail.store": storeService,
                    "discuss.voice_message": voiceMessageService,
                    multi_tab: multiTabService,
                    bus_service: busService,
                    "bus.parameters": busParametersService,
                    file_upload: fileUploadService,
                };
                for (const [serviceName, service] of Object.entries(REQUIRED_SERVICES)) {
                    if (!serviceRegistry.contains(serviceName)) {
                        serviceRegistry.add(serviceName, service);
                    }
                }
                patchWithCleanup(PrescriptionsListRenderer, {
                    init() {
                        super.init(...arguments);
                        this.LONG_TOUCH_THRESHOLD = 0;
                    },
                });
            },
        },
        function () {
            QUnit.module("PrescriptionsKanbanViewMobile", function () {
                QUnit.test("basic rendering on mobile", async function (assert) {
                    assert.expect(11);

                    const pyEnv = await startServer();
                    const prescriptionsFolderId1 = pyEnv["prescriptions.folder"].create({
                        name: "Workspace1",
                        description: "_F1-test-description_",
                        has_write_access: true,
                    });
                    pyEnv["prescriptions.prescription"].create([
                        {
                            folder_id: prescriptionsFolderId1,
                            name: "gnap",
                        },
                        {
                            folder_id: prescriptionsFolderId1,
                            name: "yop",
                        },
                    ]);
                    const views = {
                        "prescriptions.prescription,false,kanban": `<kanban js_class="prescriptions_kanban">
                    <templates>
                        <t t-name="kanban-box">
                            <div>
                                <i class="fa fa-circle-thin o_record_selector"/>
                                <field name="name"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
                    };
                    const { openView } = await createPrescriptionsViewWithMessaging({
                        serverData: { views },
                    });
                    await openView({
                        res_model: "prescriptions.prescription",
                        views: [[false, "kanban"]],
                    });

                    assert.containsOnce(
                        target,
                        ".o_prescriptions_kanban_view",
                        "should have a prescriptions kanban view"
                    );
                    assert.containsOnce(
                        target,
                        ".o_prescriptions_inspector",
                        "should have a prescriptions inspector"
                    );

                    const controlPanelButtons = target.querySelector(
                        ".o_control_panel .o_cp_buttons"
                    );
                    assert.containsNone(
                        controlPanelButtons,
                        "> .btn",
                        "there should be no button left in the ControlPanel's left part"
                    );

                    // open search panel
                    await click(target, ".o_search_panel_current_selection");
                    await nextTick();
                    // select global view
                    let searchPanel = prescription.querySelector(".o_search_panel");
                    await click(
                        searchPanel,
                        ".o_search_panel_category_value:nth-of-type(1) header"
                    );
                    // close search panel
                    await click(searchPanel, ".o_mobile_search_footer");

                    assert.containsOnce(
                        target.querySelector(".o_cp_buttons"),
                        ".o_prescriptions_kanban_upload.pe-none.opacity-25",
                        "the upload button should be disabled on global view"
                    );

                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_url").disabled,
                        "the upload url button should be disabled on global view"
                    );
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_request").disabled,
                        "the request button should be disabled on global view"
                    );

                    await click(target, ".o_kanban_record:nth-of-type(1) .o_record_selector");
                    assert.ok(
                        target.querySelector(".o_prescriptions_kanban_share_domain").disabled === false,
                        "the share button should be enabled on global view when prescriptions are selected"
                    );

                    // open search panel
                    await click(target, ".o_search_panel_current_selection");
                    // select first folder
                    searchPanel = prescription.querySelector(".o_search_panel");
                    await click(
                        searchPanel,
                        ".o_search_panel_category_value:nth-of-type(2) header"
                    );
                    // close search panel
                    await click(searchPanel, ".o_mobile_search_footer");
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_upload").disabled,
                        "the upload button should be enabled when a folder is selected"
                    );
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_url").disabled,
                        "the upload url button should be enabled when a folder is selected"
                    );
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_request").disabled,
                        "the request button should be enabled when a folder is selected"
                    );
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_share_domain").disabled,
                        "the share button should be enabled when a folder is selected"
                    );
                });

                QUnit.module("PrescriptionsInspector");

                QUnit.test("toggle inspector based on selection", async function (assert) {
                    assert.expect(13);

                    const pyEnv = await startServer();
                    const prescriptionsFolderId1 = pyEnv["prescriptions.folder"].create({
                        name: "Workspace1",
                        description: "_F1-test-description_",
                    });
                    pyEnv["prescriptions.prescription"].create([
                        { folder_id: prescriptionsFolderId1 },
                        { folder_id: prescriptionsFolderId1 },
                    ]);
                    const views = {
                        "prescriptions.prescription,false,kanban": `<kanban js_class="prescriptions_kanban">
                    <templates>
                        <t t-name="kanban-box">
                            <div>
                                <i class="fa fa-circle-thin o_record_selector"/>
                                <field name="name"/>
                            </div>
                        </t>
                    </templates>
                </kanban>`,
                    };
                    const { openView } = await createPrescriptionsViewWithMessaging({
                        serverData: { views },
                    });
                    await openView({
                        res_model: "prescriptions.prescription",
                        views: [[false, "kanban"]],
                    });

                    assert.isNotVisible(
                        prescription.querySelector(".o_prescriptions_mobile_inspector"),
                        "inspector should be hidden when selection is empty"
                    );
                    assert.containsN(
                        prescription.body,
                        ".o_kanban_record:not(.o_kanban_ghost)",
                        2,
                        "should have 2 records in the renderer"
                    );

                    // select a first record
                    await click(prescription.querySelector(".o_kanban_record .o_record_selector"));
                    assert.containsOnce(
                        prescription.body,
                        ".o_kanban_record.o_record_selected:not(.o_kanban_ghost)",
                        "should have 1 record selected"
                    );
                    const toggleInspectorSelector =
                        ".o_prescriptions_mobile_inspector > .o_prescriptions_toggle_inspector";
                    assert.isVisible(
                        prescription.querySelector(toggleInspectorSelector),
                        "toggle inspector's button should be displayed when selection is not empty"
                    );
                    assert.strictEqual(
                        prescription
                            .querySelector(toggleInspectorSelector)
                            .innerText.replace(/\s+/g, " ")
                            .trim(),
                        "1 prescription selected"
                    );

                    assert.isVisible(
                        prescription.querySelector(".o_prescriptions_mobile_inspector"),
                        "inspector should be opened"
                    );

                    await click(prescription.querySelector(".o_prescriptions_close_inspector"));
                    assert.isNotVisible(
                        prescription.querySelector(".o_prescriptions_mobile_inspector"),
                        "inspector should be closed"
                    );

                    // select a second record
                    await click(
                        prescription.querySelectorAll(".o_kanban_record .o_record_selector")[1]
                    );
                    await nextTick();
                    assert.containsN(
                        prescription.body,
                        ".o_kanban_record.o_record_selected:not(.o_kanban_ghost)",
                        2,
                        "should have 2 records selected"
                    );
                    assert.strictEqual(
                        prescription
                            .querySelector(toggleInspectorSelector)
                            .innerText.replace(/\s+/g, " ")
                            .trim(),
                        "2 prescriptions selected"
                    );

                    // click on the record
                    await click(prescription.querySelector(".o_kanban_record"));
                    await nextTick();
                    assert.containsOnce(
                        prescription.body,
                        ".o_kanban_record.o_record_selected:not(.o_kanban_ghost)",
                        "should have 1 record selected"
                    );
                    assert.strictEqual(
                        prescription
                            .querySelector(toggleInspectorSelector)
                            .innerText.replace(/\s+/g, " ")
                            .trim(),
                        "1 prescription selected"
                    );
                    assert.isVisible(
                        prescription.querySelector(".o_prescriptions_mobile_inspector"),
                        "inspector should be opened"
                    );

                    // close inspector
                    await click(prescription.querySelector(".o_prescriptions_close_inspector"));
                    assert.containsOnce(
                        prescription.body,
                        ".o_kanban_record.o_record_selected:not(.o_kanban_ghost)",
                        "should still have 1 record selected after closing inspector"
                    );
                });
            });

            QUnit.module("PrescriptionsListViewMobile", function () {
                QUnit.test("basic rendering on mobile", async function (assert) {
                    assert.expect(11);

                    const pyEnv = await startServer();
                    const prescriptionsFolderId1 = pyEnv["prescriptions.folder"].create({
                        name: "Workspace1",
                        description: "_F1-test-description_",
                        has_write_access: true,
                    });
                    pyEnv["prescriptions.prescription"].create([
                        {
                            folder_id: prescriptionsFolderId1,
                            name: "gnap",
                        },
                        {
                            folder_id: prescriptionsFolderId1,
                            name: "yop",
                        },
                    ]);
                    const views = {
                        "prescriptions.prescription,false,list": `
                        <tree js_class="prescriptions_list">
                            <field name="name"/>
                        </tree>`,
                    };
                    const { openView } = await createPrescriptionsViewWithMessaging({
                        serverData: { views },
                    });
                    await openView({
                        res_model: "prescriptions.prescription",
                        views: [[false, "list"]],
                    });

                    assert.containsOnce(
                        target,
                        ".o_prescriptions_list_view",
                        "should have a prescriptions kanban view"
                    );
                    assert.containsOnce(
                        target,
                        ".o_prescriptions_inspector",
                        "should have a prescriptions inspector"
                    );

                    const controlPanelButtons = target.querySelector(
                        ".o_control_panel .o_cp_buttons"
                    );
                    assert.containsNone(
                        controlPanelButtons,
                        "> .btn",
                        "there should be no button left in the ControlPanel's left part"
                    );
                    // open search panel
                    await click(target, ".o_search_panel_current_selection");
                    await nextTick();
                    // select global view
                    let searchPanel = prescription.querySelector(".o_search_panel");
                    await click(
                        searchPanel,
                        ".o_search_panel_category_value:nth-of-type(1) header"
                    );
                    // close search panel
                    await click(searchPanel, ".o_mobile_search_footer");
                    assert.containsOnce(
                        target.querySelector(".o_cp_buttons"),
                        ".o_prescriptions_kanban_upload.pe-none.opacity-25",
                        "the upload button should be disabled on global view"
                    );
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_url").disabled,
                        "the upload url button should be disabled on global view"
                    );
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_request").disabled,
                        "the request button should be disabled on global view"
                    );

                    await click(target, ".o_data_row:nth-of-type(1) .o_list_record_selector");
                    assert.ok(
                        target.querySelector(".o_prescriptions_kanban_share_domain").disabled === false,
                        "the share button should be enabled on global view when prescriptions are selected"
                    );

                    // open search panel
                    await click(target, ".o_search_panel_current_selection");
                    // select first folder
                    searchPanel = prescription.querySelector(".o_search_panel");
                    await click(
                        searchPanel,
                        ".o_search_panel_category_value:nth-of-type(2) header"
                    );
                    // close search panel
                    await click(searchPanel, ".o_mobile_search_footer");
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_upload").disabled,
                        "the upload button should be enabled when a folder is selected"
                    );
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_url").disabled,
                        "the upload url button should be enabled when a folder is selected"
                    );
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_request").disabled,
                        "the request button should be enabled when a folder is selected"
                    );
                    assert.notOk(
                        target.querySelector(".o_prescriptions_kanban_share_domain").disabled,
                        "the share button should be enabled when a folder is selected"
                    );
                });

                QUnit.module("PrescriptionsInspector");

                QUnit.test("toggle inspector based on selection", async function (assert) {
                    assert.expect(15);

                    const pyEnv = await startServer();
                    const prescriptionsFolderId1 = pyEnv["prescriptions.folder"].create({
                        name: "Workspace1",
                        description: "_F1-test-description_",
                    });
                    pyEnv["prescriptions.prescription"].create([
                        { folder_id: prescriptionsFolderId1 },
                        { folder_id: prescriptionsFolderId1 },
                    ]);
                    const views = {
                        "prescriptions.prescription,false,list": `<tree js_class="prescriptions_list">
                    <field name="name"/>
                </tree>`,
                    };
                    const { openView } = await createPrescriptionsViewWithMessaging({
                        touchScreen: true,
                        serverData: { views },
                    });
                    await openView({
                        res_model: "prescriptions.prescription",
                        views: [[false, "list"]],
                    });

                    assert.isNotVisible(
                        prescription.querySelector(".o_prescriptions_mobile_inspector"),
                        "inspector should be hidden when selection is empty"
                    );
                    assert.containsN(
                        prescription.body,
                        ".o_data_row",
                        2,
                        "should have 2 records in the renderer"
                    );

                    // select a first record (enter selection mode)
                    await click(prescription.querySelector(".o_data_row"));
                    const toggleInspectorSelector =
                        ".o_prescriptions_mobile_inspector > .o_prescriptions_toggle_inspector";
                    assert.isVisible(
                        prescription.querySelector(
                            ".o_prescriptions_mobile_inspector > *:not(.o_prescriptions_toggle_inspector)"
                        ),
                        "inspector should be opened"
                    );

                    await click(prescription.querySelector(".o_prescriptions_close_inspector"));
                    assert.isNotVisible(
                        prescription.querySelector(
                            ".o_prescriptions_mobile_inspector > *:not(.o_prescriptions_toggle_inspector)"
                        ),
                        "inspector should be closed"
                    );

                    assert.isVisible(
                        prescription.querySelector(toggleInspectorSelector),
                        "toggle inspector's button should be displayed when selection is not empty"
                    );
                    assert.strictEqual(
                        prescription
                            .querySelector(toggleInspectorSelector)
                            .innerText.replace(/\s+/g, " ")
                            .trim(),
                        "1 prescription selected"
                    );
                    assert.containsOnce(
                        prescription.body,
                        ".o_data_row.o_data_row_selected",
                        "should have 1 record selected"
                    );

                    // select a second record
                    await click(prescription.querySelector(".o_data_row:nth-child(2)"));
                    assert.containsN(
                        prescription.body,
                        ".o_data_row.o_data_row_selected",
                        2,
                        "should have 2 records selected"
                    );
                    assert.strictEqual(
                        prescription
                            .querySelector(toggleInspectorSelector)
                            .innerText.replace(/\s+/g, " ")
                            .trim(),
                        "2 prescriptions selected"
                    );
                    assert.isNotVisible(
                        prescription.querySelector(
                            ".o_prescriptions_mobile_inspector > *:not(.o_prescriptions_toggle_inspector)"
                        ),
                        "inspector should stay closed"
                    );

                    // disable selection mode
                    await click(prescription.querySelector(".o_list_unselect_all"));
                    assert.containsNone(
                        prescription.body,
                        ".o_prescription_list_record.o_data_row_selected",
                        "shouldn't have record selected"
                    );

                    // click on the record
                    await click(prescription.querySelector(".o_data_row"));
                    assert.containsOnce(
                        prescription.body,
                        ".o_data_row.o_data_row_selected",
                        "should have 1 record selected"
                    );
                    assert.strictEqual(
                        prescription
                            .querySelector(toggleInspectorSelector)
                            .innerText.replace(/\s+/g, " ")
                            .trim(),
                        "1 prescription selected"
                    );
                    assert.isVisible(
                        prescription.querySelector(
                            ".o_prescriptions_mobile_inspector > *:not(.o_prescriptions_toggle_inspector)"
                        ),
                        "inspector should be opened"
                    );

                    // close inspector
                    await click(prescription.querySelector(".o_prescriptions_close_inspector"));
                    assert.containsOnce(
                        prescription.body,
                        ".o_data_row .o_list_record_selector input:checked",
                        "should still have 1 record selected after closing inspector"
                    );
                });
            });
        }
    );
});
