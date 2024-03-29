/** @odoo-module **/

    import StandaloneFieldManagerMixin from 'web.StandaloneFieldManagerMixin';
    import Widget from 'web.Widget';

    import { Many2OneAvatarPractitioner } from '@pod_manager/js/m2x_avatar_practitioner';

    const StandaloneM2OAvatarPractitioner = Widget.extend(StandaloneFieldManagerMixin, {
        className: 'o_standalone_avatar_practitioner',

        /**
         * @override
         */
        init(parent, value) {
            this._super(...arguments);
            StandaloneFieldManagerMixin.init.call(this);
            this.value = value;
        },
        /**
         * @override
         */
        willStart() {
            return Promise.all([this._super(...arguments), this._makeAvatarWidget()]);
        },
        /**
         * @override
         */
        start() {
            this.avatarWidget.$el.appendTo(this.$el);
            return this._super(...arguments);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Create a record, and initialize and start the avatar widget.
         *
         * @private
         * @returns {Promise}
         */
        async _makeAvatarWidget() {
            const modelName = 'pod.practitioner';
            const fieldName = 'practitioner_id';
            const recordId = await this.model.makeRecord(modelName, [{
                name: fieldName,
                relation: modelName,
                type: 'many2one',
                value: this.value,
            }]);
            const state = this.model.get(recordId);
            this.avatarWidget = new Many2OneAvatarPractitioner(this, fieldName, state);
            this._registerWidget(recordId, fieldName, this.avatarWidget);
            return this.avatarWidget.appendTo(document.createDocumentFragment());
        },
    });

    export default StandaloneM2OAvatarPractitioner;
