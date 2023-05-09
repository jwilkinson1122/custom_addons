/** @odoo-module **/

import {
    registerInstancePatchModel,
} from '@mail/model/model_core';

registerInstancePatchModel('mail.messaging', 'podiatry/static/src/models/messaging/messaging.js', {
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     * @param {integer} [param0.employeeId]
     */
    async getChat({ employeeId }) {
        if (employeeId) {
            const employee = this.messaging.models['podiatry.employee'].insert({ id: employeeId });
            return employee.getChat();
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    async openProfile({ id, model }) {
        if (model === 'podiatry.employee' || model === 'podiatry.employee.public') {
            const employee = this.messaging.models['podiatry.employee'].insert({ id });
            return employee.openProfile(model);
        }
        return this._super(...arguments);
    },
});
