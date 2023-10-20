/** @odoo-module **/

import { registerNewModel } from '@mail/model/model_core';
import { attr, one2one } from '@mail/model/model_field';
import { insert, unlink } from '@mail/model/model_field_command';

function factory(dependencies) {

    class Practitioner extends dependencies['mail.model'] {

        //----------------------------------------------------------------------
        // Public
        //----------------------------------------------------------------------

        /**
         * @static
         * @param {Object} data
         * @returns {Object}
         */
        static convertData(data) {
            const data2 = {};
            if ('id' in data) {
                data2.id = data.id;
            }
            if ('user_id' in data) {
                data2.hasCheckedUser = true;
                if (!data.user_id) {
                    data2.user = unlink();
                } else {
                    const partnerNameGet = data['user_partner_id'];
                    const partnerData = {
                        display_name: partnerNameGet[1],
                        id: partnerNameGet[0],
                    };
                    const userNameGet = data['user_id'];
                    const userData = {
                        id: userNameGet[0],
                        partner: insert(partnerData),
                        display_name: userNameGet[1],
                    };
                    data2.user = insert(userData);
                }
            }
            return data2;
        }

        /**
         * Performs the `read` RPC on the `pod.practitioner.public`.
         *
         * @static
         * @param {Object} param0
         * @param {Object} param0.context
         * @param {string[]} param0.fields
         * @param {integer[]} param0.ids
         */
        static async performRpcRead({ context, fields, ids }) {
            const practitionersData = await this.env.services.rpc({
                model: 'pod.practitioner.public',
                method: 'read',
                args: [ids, fields],
                kwargs: {
                    context,
                },
            });
            this.messaging.models['pod.practitioner'].insert(practitionersData.map(practitionerData =>
                this.messaging.models['pod.practitioner'].convertData(practitionerData)
            ));
        }

        /**
         * Performs the `search_read` RPC on `pod.practitioner.public`.
         *
         * @static
         * @param {Object} param0
         * @param {Object} param0.context
         * @param {Array[]} param0.domain
         * @param {string[]} param0.fields
         */
        static async performRpcSearchRead({ context, domain, fields }) {
            const practitionersData = await this.env.services.rpc({
                model: 'pod.practitioner.public',
                method: 'search_read',
                kwargs: {
                    context,
                    domain,
                    fields,
                },
            });
            this.messaging.models['pod.practitioner'].insert(practitionersData.map(practitionerData =>
                this.messaging.models['pod.practitioner'].convertData(practitionerData)
            ));
        }

        /**
         * Checks whether this practitioner has a related user and partner and links
         * them if applicable.
         */
        async checkIsUser() {
            return this.messaging.models['pod.practitioner'].performRpcRead({
                ids: [this.id],
                fields: ['user_id', 'user_partner_id'],
                context: { active_test: false },
            });
        }

        /**
         * Gets the chat between the user of this practitioner and the current user.
         *
         * If a chat is not appropriate, a notification is displayed instead.
         *
         * @returns {mail.thread|undefined}
         */
        async getChat() {
            if (!this.user && !this.hasCheckedUser) {
                await this.async(() => this.checkIsUser());
            }
            // prevent chatting with non-users
            if (!this.user) {
                this.env.services['notification'].notify({
                    message: this.env._t("You can only chat with practitioners that have a dedicated user."),
                    type: 'info',
                });
                return;
            }
            return this.user.getChat();
        }

        /**
         * Opens a chat between the user of this practitioner and the current user
         * and returns it.
         *
         * If a chat is not appropriate, a notification is displayed instead.
         *
         * @param {Object} [options] forwarded to @see `mail.thread:open()`
         * @returns {mail.thread|undefined}
         */
        async openChat(options) {
            const chat = await this.async(() => this.getChat());
            if (!chat) {
                return;
            }
            await this.async(() => chat.open(options));
            return chat;
        }

        /**
         * Opens the most appropriate view that is a profile for this practitioner.
         */
        async openProfile(model = 'pod.practitioner.public') {
            return this.messaging.openDocument({
                id: this.id,
                model: model,
            });
        }

    }

    Practitioner.fields = {
        /**
         * Whether an attempt was already made to fetch the user corresponding
         * to this practitioner. This prevents doing the same RPC multiple times.
         */
        hasCheckedUser: attr({
            default: false,
        }),
        /**
         * Unique identifier for this practitioner.
         */
        id: attr({
            readonly: true,
            required: true,
        }),
        /**
         * Partner related to this practitioner.
         */
        partner: one2one('mail.partner', {
            inverse: 'practitioner',
            related: 'user.partner',
        }),
        /**
         * User related to this practitioner.
         */
        user: one2one('mail.user', {
            inverse: 'practitioner',
        }),
    };
    Practitioner.identifyingFields = ['id'];
    Practitioner.modelName = 'pod.practitioner';

    return Practitioner;
}

registerNewModel('pod.practitioner', factory);
