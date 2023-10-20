/** @odoo-module **/

import {
    registerFieldPatchModel,
} from '@mail/model/model_core';
import { one2one } from '@mail/model/model_field';

registerFieldPatchModel('mail.user', 'pod_manager/static/src/models/user/user.js', {
    /**
     * Practitioner related to this user.
     */
    practitioner: one2one('pod.practitioner', {
        inverse: 'user',
    }),
});

