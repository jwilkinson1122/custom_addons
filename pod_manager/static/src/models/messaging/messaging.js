/** @odoo-module **/

import {
    registerInstancePatchModel,
} from '@mail/model/model_core';

registerInstancePatchModel('mail.messaging', 'pod_manager/static/src/models/messaging/messaging.js', {
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     * @param {integer} [param0.practitionerId]
     */
    async getChat({ practitionerId }) {
        if (practitionerId) {
            const practitioner = this.messaging.models['pod.practitioner'].insert({ id: practitionerId });
            return practitioner.getChat();
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    async openProfile({ id, model }) {
        if (model === 'pod.practitioner' || model === 'pod.practitioner.public') {
            const practitioner = this.messaging.models['pod.practitioner'].insert({ id });
            return practitioner.openProfile(model);
        }
        return this._super(...arguments);
    },
});
