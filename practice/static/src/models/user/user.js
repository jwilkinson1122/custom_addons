/** @odoo-module **/

import {
    registerFieldPatchModel,
} from '@mail/model/model_core';
import { one2one } from '@mail/model/model_field';

registerFieldPatchModel('mail.user', 'podiatry/static/src/models/user/user.js', {
    /**
     * Employee related to this user.
     */
    employee: one2one('podiatry.employee', {
        inverse: 'user',
    }),
});

