/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useBus, useService } from "@web/core/utils/hooks";
import { escape } from "@web/core/utils/strings";
import { memoize } from "@web/core/utils/functions";
import { formatFloat } from "@web/core/utils/numbers";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { useSetupView } from "@web/views/view_hook";
import { PdfManager } from "@prescriptions/owl/components/pdf_manager/pdf_manager";
import { x2ManyCommands } from "@web/core/orm_service";
import { EventBus, onWillStart, markup, useComponent, useEnv, useRef, useSubEnv } from "@odoo/owl";

/**
 * Controller/View hooks
 */

export async function toggleArchive(model, resModel, resIds, doArchive) {
    const action = await model.orm.call(
        resModel,
        doArchive ? "action_archive" : "action_unarchive",
        [resIds]
    );
    if (action && Object.keys(action).length !== 0) {
        model.action.doAction(action);
    }
    await model.load();
    await model.notify();
}

export function preSuperSetupFolder() {
    const component = useComponent();
    const orm = useService("orm");
    onWillStart(async () => {
        component._deletionDelay = await orm.call("prescriptions.prescription", "get_deletion_delay", [[]]);
    });
}

// Small hack, memoize uses the first argument as cache key, but we need the orm which will not be the same.
const loadMaxUploadSize = memoize((_null, orm) =>
    orm.call("prescriptions.prescription", "get_prescription_max_upload_limit")
);

/**
 * To be executed before calling super.setup in view controllers.
 */
export function preSuperSetup() {
    // Otherwise not available in model.env
    useSubEnv({
        prescriptionsView: {
            bus: new EventBus(),
        },
    });
    const component = useComponent();
    const props = component.props;
    // Root state is shared between views to keep the selection
    if (props.globalState && props.globalState.sharedSelection) {
        if (!props.state) {
            props.state = {};
        }
        if (!props.state.modelState) {
            props.state.modelState = {};
        }
        props.state.modelState.sharedSelection = props.globalState.sharedSelection;
    }
}

/**
 * Sets up the env required by prescriptions view, as well as any other hooks.
 * Returns properties to be applied to the calling component. The code assumes that those properties are assigned to the component.
 */
export function usePrescriptionView(helpers) {
    const component = useComponent();
    const props = component.props;
    const root = useRef("root");
    const orm = useService("orm");
    const notification = useService("notification");
    const dialogService = useService("dialog");
    const action = useService("action");

    // Env setup
    useSubEnv({
        model: component.model,
    });
    const env = useEnv();

    // Keep selection between views
    useSetupView({
        rootRef: root,
        getGlobalState: () => ({
            sharedSelection: component.model.exportSelection(),
        }),
    });

    let maxUploadSize;
    Object.defineProperty(component, "maxUploadSize", {
        get: () => maxUploadSize,
        set: (newVal) => {
            maxUploadSize = newVal;
        },
    });
    onWillStart(async () => {
        component.maxUploadSize = await loadMaxUploadSize(null, orm);
    });

    return {
        // Refs
        root,
        // Services
        orm,
        notification,
        dialogService,
        actionService: action,
        // Prescription preview
        ...usePrescriptionsViewFilePreviewer(helpers),
        // Prescription upload
        ...usePrescriptionsViewFileUpload(),
        // Trigger rule
        ...useTriggerRule(),
        // Helpers
        hasSharePrescriptions: () => {
            const folder = env.searchModel.getSelectedFolder();
            const selectedRecords = env.model.root.selection.length;
            return !folder.id && !selectedRecords;
        },
        // Listeners
        onClickPrescriptionsRequest: () => {
            action.doAction("prescriptions.action_request_form", {
                additionalContext: {
                    default_partner_id: props.context.default_partner_id || false,
                    default_folder_id:
                        env.searchModel.getSelectedFolderId() || env.searchModel.getFolders()[1].id,
                    default_tag_ids: [x2ManyCommands.set(env.searchModel.getSelectedTagIds())],
                    default_res_id: props.context.default_res_id || false,
                    default_res_model: props.context.default_res_model || false,
                },
                fullscreen: env.isSmall,
                onClose: async () => {
                    await env.model.load();
                    env.model.useSampleModel = env.model.root.records.length === 0;
                    env.model.notify();
                },
            });
        },
        onClickPrescriptionsAddUrl: () => {
            action.doAction("prescriptions.action_url_form", {
                additionalContext: {
                    default_partner_id: props.context.default_partner_id || false,
                    default_folder_id: env.searchModel.getSelectedFolderId(),
                    default_tag_ids: [x2ManyCommands.set(env.searchModel.getSelectedTagIds())],
                    default_res_id: props.context.default_res_id || false,
                    default_res_model: props.context.default_res_model || false,
                },
                fullscreen: env.isSmall,
                onClose: async () => {
                    await env.model.load();
                    env.model.useSampleModel = env.model.root.records.length === 0;
                    env.model.notify();
                },
            });
        },
        onClickShareDomain: async () => {
            const selection = env.model.root.selection;
            const folderId = env.searchModel.getSelectedFolderId();
            if (
                selection.length &&
                selection.every((rec) => ["empty", "url"].includes(rec._values.type))
            ) {
                notification.add(_t("The links and requested prescriptions are not shareable."), {
                    type: "danger",
                });
                return;
            }
            // All workspace
            let folderIds;
            if (!folderId) {
                folderIds = selection
                    .filter((rec) => !["empty", "url"].includes(rec._values.type))
                    .map((rec) => rec.data.folder_id[0]);
                // Check if prescriptions are from different workspace
                if (folderIds.length > 1 && folderIds.some((val) => val !== folderIds[0])) {
                    notification.add(_t("Can't share prescriptions of different workspaces."), {
                        type: "danger",
                    });
                    return;
                }
            }
            const defaultVals = {
                domain: env.searchModel.domain,
                folder_id: folderId || folderIds[0],
                tag_ids: [x2ManyCommands.set(env.searchModel.getSelectedTagIds())],
                type: selection.length ? "ids" : "domain",
                prescription_ids: selection.length
                    ? [
                          x2ManyCommands.set(
                              selection
                                  .filter((rec) => rec._values.type !== "empty")
                                  .map((rec) => rec.resId)
                          ),
                      ]
                    : false,
            };
            const vals = helpers?.sharePopupAction
                ? await helpers.sharePopupAction(defaultVals)
                : defaultVals;
            const act = await orm.call("prescriptions.share", "open_share_popup", [vals]);
            const shareResId = act.res_id;
            let saved = false;
            dialogService.add(
                FormViewDialog,
                {
                    resModel: "prescriptions.share",
                    resId: shareResId,
                    onRecordSaved: async (record) => {
                        saved = true;
                        // Copy the share link to the clipboard
                        navigator.clipboard.writeText(record.data.full_url);
                        // Show a notification to the user about the copy to clipboard
                        notification.add(_t("The share url has been copied to your clipboard."), {
                            type: "success",
                        });
                    },
                },
                {
                    onClose: async () => {
                        if (!saved) {
                            await orm.unlink("prescriptions.share", [shareResId]);
                        }
                    },
                }
            );
        },
    };
}

/**
 * Hook to setup the file previewer
 */
function usePrescriptionsViewFilePreviewer({
    getSelectedPrescriptionsElements,
    setInspectedPrescriptions,
    setPreviewStore,
    isRecordPreviewable = () => true,
}) {
    const component = useComponent();
    const env = useEnv();
    const bus = env.prescriptionsView.bus;
    /** @type {import("@prescriptions/core/prescription_service").PrescriptionService} */
    const prescriptionService = useService("prescription.prescription");
    /** @type {import("@mail/core/common/store_service").Store} */
    const store = useService("mail.store");

    const onOpenPrescriptionsPreview = async ({
        prescriptions,
        mainPrescription,
        isPdfSplit,
        rules,
        hasPdfSplit,
    }) => {
        const openPdfSplitter = (prescriptions) => {
            let newPrescriptionIds = [];
            let forceDelete = false;
            component.dialogService.add(
                PdfManager,
                {
                    prescriptions: prescriptions.map((doc) => doc.data),
                    rules: rules.map((rule) => {
                        return { ...rule.data, id: rule.resId };
                    }),
                    onProcessPrescriptions: ({ prescriptionIds, ruleId, exit, isForcingDelete }) => {
                        forceDelete = isForcingDelete;
                        if (prescriptionIds && prescriptionIds.length) {
                            newPrescriptionIds = [...new Set(newPrescriptionIds.concat(prescriptionIds))];
                        }
                        if (ruleId) {
                            component.triggerRule(prescriptionIds, ruleId, !exit);
                        }
                    },
                },
                {
                    onClose: async () => {
                        if (!newPrescriptionIds.length && !forceDelete) {
                            return;
                        }
                        await component.model.load();
                        let count = 0;
                        for (const record of prescriptions) {
                            if (!newPrescriptionIds.includes(record.resId)) {
                                record.model.root.deleteRecords(record);
                                continue;
                            }
                            record.onRecordClick(null, {
                                isKeepSelection: count++ !== 0,
                                isRangeSelection: false,
                            });
                        }
                    },
                }
            );
        };
        if (isPdfSplit) {
            openPdfSplitter(prescriptions);
            return;
        }
        const prescriptionsRecords = (
            (prescriptions.length === 1 && component.model.root.records) ||
            prescriptions
        )
            .filter(isRecordPreviewable)
            .map((rec) => {
                return store.Prescription.insert({
                    id: rec.resId,
                    attachment: {
                        id: rec.data.attachment_id[0],
                        name: rec.data.attachment_id[1],
                        mimetype: rec.data.mimetype,
                        url: rec.data.url,
                        displayName: rec.data.display_name,
                        prescriptionId: rec.resId,
                    },
                    name: rec.data.name,
                    mimetype: rec.data.mimetype,
                    url: rec.data.url,
                    displayName: rec.data.display_name,
                    record: rec,
                });
            });
        // If there is a scrollbar we don't want it whenever the previewer is opened
        if (component.root.el) {
            component.root.el.querySelector(".o_prescriptions_view").classList.add("overflow-hidden");
        }
        const selectedPrescription = prescriptionsRecords.find(
            (rec) => rec.id === (mainPrescription || prescriptions[0]).resId
        );
        prescriptionService.prescriptionList = {
            prescriptions: prescriptionsRecords || [],
            initialRecordSelectionLength: prescriptions.length,
            pdfManagerOpenCallback: (prescriptions) => {
                openPdfSplitter(prescriptions);
            },
            onDeleteCallback: () => {
                // We want to focus on the first selected prescription's element
                const elements = getSelectedPrescriptionsElements();
                if (elements.length) {
                    elements[0].focus();
                }
                if (component.root.el) {
                    component.root.el
                        .querySelector(".o_prescriptions_view")
                        .classList.remove("overflow-hidden");
                }

                setInspectedPrescriptions([]);
                setPreviewStore({});
            },
            onSelectPrescription: (record) => {
                // change the inspected prescriptions only if we inspect only one
                if (prescriptions.length <= 1) {
                    setInspectedPrescriptions([record]);
                }
            },
            hasPdfSplit,
            selectedPrescription,
        };

        const previewStore = {
            prescriptionList: prescriptionService.prescriptionList,
            startIndex: prescriptionsRecords.indexOf(selectedPrescription),
            attachments: prescriptionsRecords.map((doc) => doc.attachment),
        };

        setInspectedPrescriptions(prescriptions);
        setPreviewStore({ ...previewStore });
    };

    useBus(bus, "prescriptions-open-preview", async (ev) => {
        component.onOpenPrescriptionsPreview(ev.detail);
    });
    useBus(bus, "prescriptions-close-preview", () => {
        setInspectedPrescriptions([]);
        setPreviewStore({});
    });

    return {
        onOpenPrescriptionsPreview,
    };
}

/**
 * Hook to setup file upload
 */
function usePrescriptionsViewFileUpload() {
    const component = useComponent();
    const env = useEnv();
    const bus = env.prescriptionsView.bus;
    const notification = useService("notification");
    const fileUpload = useService("file_upload");

    const handleUploadError = (result) => {
        notification.add(result.error, {
            title: _t("Error"),
            sticky: true,
        });
    };

    let wasUsingSampleModel = false;
    useBus(fileUpload.bus, "FILE_UPLOAD_ADDED", () => {
        if (env.model.useSampleModel) {
            wasUsingSampleModel = true;
            env.model.useSampleModel = false;
        }
    });

    useBus(fileUpload.bus, "FILE_UPLOAD_ERROR", async (ev) => {
        const { upload } = ev.detail;
        if (wasUsingSampleModel) {
            wasUsingSampleModel = false;
            env.model.useSampleModel = true;
        }
        if (upload.state !== "error") {
            return;
        }
        handleUploadError({
            error: _t("An error occured while uploading."),
        });
    });

    useBus(fileUpload.bus, "FILE_UPLOAD_LOADED", async (ev) => {
        wasUsingSampleModel = false;
        const { upload } = ev.detail;
        const xhr = upload.xhr;
        const result =
            xhr.status === 200
                ? JSON.parse(xhr.response)
                : { error: _t("status code: %s, message: %s", xhr.status, xhr.response) };
        if (result.error) {
            handleUploadError(result);
        } else {
            env.model.useSampleModel = false;
            await env.model.load();
            if (!result.ids) {
                return;
            }
            const records = env.model.root.records;
            let count = 0;
            for (const record of records) {
                if (!result.ids.includes(record.resId)) {
                    continue;
                }
                record.onRecordClick(null, {
                    isKeepSelection: count++ !== 0,
                    isRangeSelection: false,
                });
            }
        }
    });

    const uploadFiles = async ({ files, folderId, recordId, context, tagIds }) => {
        const validFiles = component.maxUploadSize
            ? [...files].filter((file) => file.size <= component.maxUploadSize)
            : files;
        if (validFiles.length !== 0) {
            await fileUpload.upload("/prescriptions/upload_attachment", validFiles, {
                buildFormData: (formData) => {
                    formData.append("folder_id", folderId);
                    if (recordId) {
                        formData.append("prescription_id", recordId);
                    }
                    if (!tagIds.length && context?.default_tag_ids) {
                        tagIds = context.default_tag_ids;
                    }
                    formData.append("tag_ids", tagIds);
                    if (context) {
                        for (const key of [
                            "default_owner_id",
                            "default_partner_id",
                            "default_res_id",
                            "default_res_model",
                        ]) {
                            if (context[key]) {
                                formData.append(key.replace("default_", ""), context[key]);
                            }
                        }
                    }
                },
                displayErrorNotification: false,
            });
        }
        if (validFiles.length < files.length) {
            const message = _t(
                "Some files could not be uploaded (max size: %s).",
                formatFloat(component.maxUploadSize, { humanReadable: true })
            );
            return notification.add(message, { type: "danger" });
        }
    };

    useBus(bus, "prescriptions-upload-files", (ev) => {
        ev.detail.context = ev.detail.context || component.props.context;
        component.uploadFiles(ev.detail);
    });

    return {
        uploadFiles,
        onFileInputChange: async (ev) => {
            if (!ev.target.files.length) {
                return;
            }
            await component.uploadFiles({
                files: ev.target.files,
                folderId: env.searchModel.getSelectedFolderId(),
                recordId: false,
                context: component.props.context,
                tagIds: env.searchModel.getSelectedTagIds(),
            });
            ev.target.value = "";
        },
    };
}

/**
 * Trigger rule hook.
 * NOTE: depends on env.model being set
 */
export function useTriggerRule() {
    const env = useEnv();
    const orm = useService("orm");
    const notification = useService("notification");
    const action = useService("action");
    return {
        triggerRule: async (prescriptionIds, ruleId, preventReload = false) => {
            const result = await orm.call("prescriptions.workflow.rule", "apply_actions", [
                [ruleId],
                prescriptionIds,
            ]);
            if (result && typeof result === "object") {
                if (Object.prototype.hasOwnProperty.call(result, "warning")) {
                    notification.add(
                        markup(
                            `<ul>${result["warning"]["prescriptions"]
                                .map((d) => `<li>${escape(d)}</li>`)
                                .join("")}</ul>`
                        ),
                        {
                            title: result["warning"]["title"],
                            type: "danger",
                        }
                    );
                    if (!preventReload) {
                        await env.model.load();
                    }
                } else if (!preventReload) {
                    await action.doAction(result, {
                        onClose: async () => await env.model.load(),
                    });
                    return;
                }
            } else if (!preventReload) {
                await env.model.load();
            }
        },
    };
}
