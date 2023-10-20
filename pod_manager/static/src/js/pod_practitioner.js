odoo.define('pod_manager.practitioner_chat', function (require) {
'use strict';
    var viewRegistry = require('web.view_registry');

    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var FormRenderer = require('web.FormRenderer');

    const ListController = require('web.ListController');
    const ListView = require('web.ListView');

    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var KanbanRenderer = require('web.KanbanRenderer');
    var KanbanRecord = require('web.KanbanRecord');

    const ChatMixin = require('pod_manager.chat_mixin');


    const core = require('web.core');
    const _t = core._t;

    // USAGE OF CHAT MIXIN IN FORM VIEWS
    var PractitionerFormRenderer = FormRenderer.extend(ChatMixin);

    const PractitionerArchiveMixin = {
        _getArchiveAction: function (id) {
            return {
                type: 'ir.actions.act_window',
                name: _t('Practitioner Termination'),
                res_model: 'pod.deactivate.wizard',
                views: [[false, 'form']],
                view_mode: 'form',
                target: 'new',
                context: {
                    'active_id': id,
                    'toggle_active': true,
                }
            }
        }
    };

    const PractitionerFormController = FormController.extend(PractitionerArchiveMixin, {
        /**
         * Override the archive action to directly open the deactivate wizard
         * @override
         * @private
         */
        _getActionMenuItems: function (state) {
            let self = this;
            let actionMenuItems = this._super(...arguments);
            const activeField = this.model.getActiveField(state);
            if (actionMenuItems != null && this.archiveEnabled && activeField in state.data) {
                //This might break in future version, don't see a better way however
                let archiveString = _t("Archive");
                let archiveMenuItem = actionMenuItems.items.other.find(item => {return (item.description === archiveString)});
                if (archiveMenuItem) {
                    archiveMenuItem.callback = () => {self.do_action(
                        self._getArchiveAction(self.model.localIdsToResIds([this.handle])[0]), {
                        on_close: function () {
                            self.update({}, {reload: true});
                        }
                    })}
                }
            }
            return actionMenuItems;
        }
    })

    var PractitionerFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: PractitionerFormController,
            Renderer: PractitionerFormRenderer
        }),
    });

    viewRegistry.add('pod_practitioner_form', PractitionerFormView);

    const PractitionerListController = ListController.extend(PractitionerArchiveMixin, {
        /**
         * Override the archive action to directly open the deactivate wizard
         * @override
         * @private
         */
        _getActionMenuItems: function (state) {
            let self = this;
            let actionMenuItems = this._super(...arguments);
            if (actionMenuItems != null && this.archiveEnabled) {
                //This might break in future version, don't see a better way however
                let archiveString = _t("Archive");
                let archiveMenuItem = actionMenuItems.items.other.find(item => {return (item.description === archiveString)});
                if (archiveMenuItem) {
                    //On this one we want the default action when multiple are selected
                    let originalCallback = archiveMenuItem.callback;
                    archiveMenuItem.callback = () => {
                        let records = self.getSelectedRecords()
                        if (records.length == 1 && records[0].data.active === true) {
                            self.do_action(
                                self._getArchiveAction(records[0].res_id), {
                                on_close: function () {
                                    self.update({}, {reload: true});
                                }
                            })
                        } else {
                            originalCallback();
                        }
                    };
                }
            }
            return actionMenuItems;
        }
    });

    const PractitionerListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: PractitionerListController,
        })
    })

    viewRegistry.add('pod_practitioner_list', PractitionerListView);

    // USAGE OF CHAT MIXIN IN KANBAN VIEWS
    var PractitionerKanbanRecord = KanbanRecord.extend(ChatMixin);

    var PractitionerKanbanRenderer = KanbanRenderer.extend({
        config: Object.assign({}, KanbanRenderer.prototype.config, {
            KanbanRecord: PractitionerKanbanRecord,
        }),
    });

    var PractitionerKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: KanbanController,
            Renderer: PractitionerKanbanRenderer
        }),
    });

    viewRegistry.add('pod_practitioner_kanban', PractitionerKanbanView);
});
