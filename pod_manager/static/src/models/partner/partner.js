/** @odoo-module **/

import {
    registerInstancePatchModel,
    registerFieldPatchModel,
} from '@mail/model/model_core';
import { attr, one2one } from '@mail/model/model_field';

registerInstancePatchModel('mail.partner', 'pod_manager/static/src/models/partner/partner.js', {
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Checks whether this partner has a related practitioner and links them if
     * applicable.
     */
    async checkIsPractitioner() {
        await this.async(() => this.messaging.models['pod.practitioner'].performRpcSearchRead({
            context: { active_test: false },
            domain: [['user_partner_id', '=', this.id]],
            fields: ['user_id', 'user_partner_id'],
        }));
        this.update({ hasCheckedPractitioner: true });
    },
    /**
     * When a partner is an practitioner, its practitioner profile contains more useful
     * information to know who he is than its partner profile.
     *
     * @override
     */
    async openProfile() {
        // limitation of patch, `this._super` becomes unavailable after `await`
        const _super = this._super.bind(this, ...arguments);
        if (!this.practitioner && !this.hasCheckedPractitioner) {
            await this.async(() => this.checkIsPractitioner());
        }
        if (this.practitioner) {
            return this.practitioner.openProfile();
        }
        return _super();
    },
});

registerFieldPatchModel('mail.partner', 'pod_manager/static/src/models/partner/partner.js', {
    /**
     * Practitioner related to this partner. It is computed through
     * the inverse relation and should be considered read-only.
     */
    practitioner: one2one('pod.practitioner', {
        inverse: 'partner',
    }),
    /**
     * Whether an attempt was already made to fetch the practitioner corresponding
     * to this partner. This prevents doing the same RPC multiple times.
     */
    hasCheckedPractitioner: attr({
        default: false,
    }),
});
