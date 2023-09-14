odoo.define("pos_validation.ir_actions_act_load_new", function (require) {
    "use strict";

    var ActionManager = require("web.ActionManager");

    ActionManager.include({
        /**
         * Intercept action handling to detect extra action type
         * @override
         */
        _handleAction: function (action, options) {
            if (action.type === "ir.actions.act_client_load_new") {
                return this._executeActionClientLoadNew(action, options);
            }
            return this._super.apply(this, arguments);
        },

        /**
         * Handle 'ir.actions.act_multi' action
         * @param {Object} action see _handleAction() parameters
         * @param {Object} options see _handleAction() parameters
         * @returns {$.Promise}
         */
        _executeActionClientLoadNew: function (action) {
            this._closeDialog();
            var controller = this.getCurrentController().widget;
            const record = controller.model.get(controller.handle, {raw: true});
            return controller.model
                .load({
                    context: record.getContext(),
                    fields: record.fields,
                    fieldsInfo: record.fieldsInfo,
                    modelName: controller.modelName,
                    res_ids: record.res_ids,
                    res_id: action.res_id,
                    type: "record",
                    viewType: "form",
                })
                .then((handle) => {
                    controller.handle = handle;
                    controller.trigger_up("reload");
                });
        },
    });
});
