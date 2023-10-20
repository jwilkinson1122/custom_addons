/** @odoo-module alias=pod_manager.Many2OneAvatarPractitioner **/

import fieldRegistry from 'web.field_registry';

import { Many2OneAvatarUser, KanbanMany2OneAvatarUser, KanbanMany2ManyAvatarUser, ListMany2ManyAvatarUser } from '@mail/js/m2x_avatar_user';
import { Many2ManyAvatarUser } from '@mail/js/m2x_avatar_user';
import { KanbanMany2ManyTagsAvatar, ListMany2ManyTagsAvatar } from 'web.relational_fields';


// This module defines variants of the Many2OneAvatarUser and Many2ManyAvatarUser
// field widgets, to support fields pointing to 'pod.practitioner'. It also defines the
// kanban version of the Many2OneAvatarPractitioner widget.
//
// Usage:
//   <field name="practitioner_id" widget="many2one_avatar_practitioner"/>

const M2XAvatarPractitionerMixin = {
    supportedModels: ['pod.practitioner', 'pod.practitioner.public'],

    //----------------------------------------------------------------------
    // Private
    //----------------------------------------------------------------------

    _getPractitionerID() {
        return this.value.res_id;
    },

    //----------------------------------------------------------------------
    // Handlers
    //----------------------------------------------------------------------

    /**
     * @override
     */
    _onAvatarClicked(ev) {
        ev.stopPropagation(); // in list view, prevent from opening the record
        const practitionerId = this._getPractitionerID(ev);
        this._openChat({ practitionerId: practitionerId });
    }
};

export const Many2OneAvatarPractitioner = Many2OneAvatarUser.extend(M2XAvatarPractitionerMixin);
export const KanbanMany2OneAvatarPractitioner = KanbanMany2OneAvatarUser.extend(M2XAvatarPractitionerMixin);

fieldRegistry.add('many2one_avatar_practitioner', Many2OneAvatarPractitioner);
fieldRegistry.add('kanban.many2one_avatar_practitioner', KanbanMany2OneAvatarPractitioner);

const M2MAvatarPractitionerMixin = Object.assign(M2XAvatarPractitionerMixin, {
    //----------------------------------------------------------------------
    // Private
    //----------------------------------------------------------------------

    _getPractitionerID(ev) {
        return parseInt(ev.target.getAttribute('data-id'), 10);
    },
});

export const Many2ManyAvatarPractitioner = Many2ManyAvatarUser.extend(M2MAvatarPractitionerMixin, {});

export const KanbanMany2ManyAvatarPractitioner = KanbanMany2ManyAvatarUser.extend(M2MAvatarPractitionerMixin, {});

export const ListMany2ManyAvatarPractitioner = ListMany2ManyAvatarUser.extend(M2MAvatarPractitionerMixin, {});

fieldRegistry.add('many2many_avatar_practitioner', Many2ManyAvatarPractitioner);
fieldRegistry.add('kanban.many2many_avatar_practitioner', KanbanMany2ManyAvatarPractitioner);
fieldRegistry.add('list.many2many_avatar_practitioner', ListMany2ManyAvatarPractitioner);

export default {
    Many2OneAvatarPractitioner,
};
