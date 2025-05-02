/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
// import { formView } from "@web/views/form/form_view";
import { ListController } from "@web/views/list/list_controller";
// import { listView } from "@web/views/list/list_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
// import { kanbanView } from "@web/views/kanban/kanban_view";
// import { pyUtils } from "@web/core/py_js/py";
import { pyUtils } from "@web/core/py_js/py_utils";
import { Component } from "@odoo/owl";

// Extending FormController
patch(FormController.prototype, {
    renderButtons($node) {
        this._super.apply(this, arguments);
        if (this._shouldHideCreateButton()) {
            this.$buttons.find(".o_form_button_create").css("display", "none");
        }
    },

    _shouldHideCreateButton() {
        return this.modelName === "product.product" && this.initialState.context.custom_create_variant;
    },

    _onButtonClicked(event) {
        const attrs = event.data.attrs;
        if (attrs.context) {
            const record_ctx = this.model.get(event.data.record.id).context;
            const btn_ctx = pyUtils.eval("context", record_ctx, attrs.context);
            this.model.localData[event.data.record.id].context = { ...btn_ctx, ...record_ctx };
        }

        if (attrs.special === "no_save") {
            this.canBeSaved = () => true;
            const event_no_save = { ...event, data: { ...event.data, attrs: { ...attrs, special: false } } };
            return this._super(event_no_save);
        }

        this._super(event);
    }
});

// Extending ListController
patch(ListController.prototype, {
    renderButtons($node) {
        this._super.apply(this, arguments);
        if (this._shouldHideAddButton()) {
            this.$buttons.find(".o_list_button_add").css("display", "none");
        }
    },

    _shouldHideAddButton() {
        return this.modelName === "product.product" && this.initialState.context.custom_create_variant;
    }
});

// Extending KanbanController
patch(KanbanController.prototype, {
    renderButtons($node) {
        this._super.apply(this, arguments);
        if (this._shouldHideNewButton()) {
            this.$buttons.find(".o-kanban-button-new").css("display", "none");
        }
    },

    _shouldHideNewButton() {
        return this.modelName === "product.product" && this.initialState.context.custom_create_variant;
    }
});


// odoo.define("product_configurator.FieldBooleanButton", function (require) {
//     "use strict";

//     var FormController = require("web.FormController");
//     var ListController = require("web.ListController");
//     var KanbanController = require("web.KanbanController");

//     var pyUtils = require("web.py_utils");

//     FormController.include({
//         renderButtons: function ($node) {
//             var self = this;
//             this._super.apply(this, arguments);
//             if (
//                 self.modelName === "product.product" &&
//                 self.initialState.context.custom_create_variant
//             ) {
//                 this.$buttons.find(".o_form_button_create").css("display", "none");
//             }
//         },

//         _onButtonClicked: function (event) {
//             var self = this;
//             var attrs = event.data.attrs;
//             if (event.data.attrs.context) {
//                 var record_ctx = self.model.get(event.data.record.id).context;
//                 var btn_ctx = pyUtils.eval(
//                     "context",
//                     record_ctx,
//                     event.data.attrs.context
//                 );
//                 self.model.localData[event.data.record.id].context = _.extend(
//                     {},
//                     btn_ctx,
//                     record_ctx
//                 );
//             }
//             if (attrs.special === "no_save") {
//                 this.canBeSaved = function () {
//                     return true;
//                 };
//                 var event_no_save = $.extend(true, {}, event);
//                 event_no_save.data.attrs.special = false;
//                 return this._super(event_no_save);
//             }
//             this._super(event);
//         },
//     });

//     ListController.include({
//         renderButtons: function ($node) {
//             var self = this;
//             this._super.apply(this, arguments);
//             if (
//                 self.modelName === "product.product" &&
//                 self.initialState.context.custom_create_variant
//             ) {
//                 this.$buttons.find(".o_list_button_add").css("display", "none");
//             }
//         },
//     });

//     KanbanController.include({
//         renderButtons: function ($node) {
//             var self = this;
//             this._super.apply(this, arguments);
//             if (
//                 self.modelName === "product.product" &&
//                 self.initialState.context.custom_create_variant
//             ) {
//                 this.$buttons.find(".o-kanban-button-new").css("display", "none");
//             }
//         },
//     });

// });


// FormController
// class ConfiguratorFormController extends FormController {
//     setup() {
//         super.setup();
//         this.orm = useService("orm");
//         this.notificationService = useService("notification");
//         // this.debouncedPrintLabel = useDebounced(this.printLabel, 200);
//     }

//     renderButtons($node) {
//         super.renderButtons($node);
//         if (
//             this.model.root.resModel === "product.product" &&
//             this.model.root.data.custom_create_variant
//         ) {
//             this.$buttons.find(".o_form_button_create").css("display", "none");
//         }
//     }

//     async _onButtonClicked(event) {
//         const attrs = event.data.attrs;
//         const recordId = this.model.root.resId;
//         if (attrs.context) {
//             const record_ctx = this.model.get(recordId).context;
//             const btn_ctx = JSON.parse(attrs.context);
//             this.model.localData[recordId].context = Object.assign({}, btn_ctx, record_ctx);
//         }

//         if (attrs.special === "no_save") {
//             this.canBeSaved = () => true;
//             const event_no_save = $.extend(true, {}, event);
//             event_no_save.data.attrs.special = false;
//             return super._onButtonClicked(event_no_save);
//         }

//         return super._onButtonClicked(event);
//     }

//     // async printLabel() {
//     //     const serverResult = await this.orm.call(this.model.root.resModel, "print_label", [
//     //         this.model.root.resId,
//     //     ]);

//     //     if (serverResult) {
//     //         this.notificationService.add(this.env._t("Label successfully printed"), {
//     //             type: "success",
//     //         });
//     //     } else {
//     //         this.notificationService.add(this.env._t("Could not print the label"), {
//     //             type: "danger",
//     //         });
//     //     }

//     //     return serverResult;
//     // }

//     // get isPrintBtnPrimary() {
//     //     return this.model.root.data && this.model.root.data.customer_id && this.model.root.data.state === "printed";
//     // }
// }

// ConfiguratorFormController.template = "product_configurator.ConfiguratorFormView";

// export const configuratorFormView = {
//     ...formView,
//     Controller: ConfiguratorFormController,
// };

// registry.category("views").add("configurator_form_view", configuratorFormView);


// ListController
// class ConfiguratorListController extends ListController {
//     setup() {
//         super.setup();
//     }

//     renderButtons($node) {
//         super.renderButtons($node);
//         if (
//             this.model.root.resModel === "product.product" &&
//             this.model.root.data.custom_create_variant
//         ) {
//             this.$buttons.find(".o_list_button_add").css("display", "none");
//         }
//     }
// }

// ConfiguratorListController.template = "product_configurator.ConfiguratorListView";

// export const configuratorListView = {
//     ...listView,
//     Controller: ConfiguratorListController,
// };

// registry.category("views").add("configurator_list_view", configuratorListView);


// KanbanController
// class ConfiguratorKanbanController extends KanbanController {
//     setup() {
//         super.setup();
//         useInterval(() => {
//             this.model.load();
//         }, 30_000);
//     }
    
//     renderButtons($node) {
//         super.renderButtons($node);
//         if (
//             this.model.root.resModel === "product.product" &&
//             this.model.root.data.custom_create_variant
//         ) {
//             this.$buttons.find(".o-kanban-button-new").css("display", "none");
//         }
//     }
// }

// ConfiguratorKanbanController.template = "product_configurator.ConfiguratorKanbanView";

// export const configuratorKanbanView = {
//     ...kanbanView,
//     Controller: ConfiguratorKanbanController,
// };

// registry.category("views").add("configurator_kanban_view", configuratorKanbanView);





// odoo.define("product_configurator.FieldBooleanButton", function (require) {
//     "use strict";

//     var FormController = require("web.FormController");
//     var ListController = require("web.ListController");
//     var KanbanController = require("web.KanbanController");

//     var pyUtils = require("web.py_utils");

//     FormController.include({
//         renderButtons: function ($node) {
//             var self = this;
//             this._super.apply(this, arguments);
//             if (
//                 self.modelName === "product.product" &&
//                 self.initialState.context.custom_create_variant
//             ) {
//                 this.$buttons.find(".o_form_button_create").css("display", "none");
//             }
//         },

//         _onButtonClicked: function (event) {
//             var self = this;
//             var attrs = event.data.attrs;
//             if (event.data.attrs.context) {
//                 var record_ctx = self.model.get(event.data.record.id).context;
//                 var btn_ctx = pyUtils.eval(
//                     "context",
//                     record_ctx,
//                     event.data.attrs.context
//                 );
//                 self.model.localData[event.data.record.id].context = _.extend(
//                     {},
//                     btn_ctx,
//                     record_ctx
//                 );
//             }
//             if (attrs.special === "no_save") {
//                 this.canBeSaved = function () {
//                     return true;
//                 };
//                 var event_no_save = $.extend(true, {}, event);
//                 event_no_save.data.attrs.special = false;
//                 return this._super(event_no_save);
//             }
//             this._super(event);
//         },
//     });

//     ListController.include({
//         renderButtons: function ($node) {
//             var self = this;
//             this._super.apply(this, arguments);
//             if (
//                 self.modelName === "product.product" &&
//                 self.initialState.context.custom_create_variant
//             ) {
//                 this.$buttons.find(".o_list_button_add").css("display", "none");
//             }
//         },
//     });

//     KanbanController.include({
//         renderButtons: function ($node) {
//             var self = this;
//             this._super.apply(this, arguments);
//             if (
//                 self.modelName === "product.product" &&
//                 self.initialState.context.custom_create_variant
//             ) {
//                 this.$buttons.find(".o-kanban-button-new").css("display", "none");
//             }
//         },
//     });

// });
