odoo.define('pod_order_management.ClientListScreen', function(require) {
    'use strict';

    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { useState } = owl.hooks;

    const BiClientListScreen = ClientListScreen =>
        class extends ClientListScreen {
            /**
             * @override
             */
            async saveChanges(event) {
                try {
                    let partnerId = await this.rpc({
                        model: 'res.partner',
                        method: 'create_partner_from_ui',
                        args: [event.detail.processedChanges,event.detail.extraprocessedChanges],
                    });
                    await this.env.pos.load_new_partners();
                    this.state.selectedClient = this.env.pos.db.get_partner_by_id(partnerId);
                    this.state.detailIsShown = false;
                    this.clickNext();
                    this.render();
                } catch (error) {
                    if (error.message.code < 0) {
                        await this.showPopup('OfflineErrorPopup', {
                            title: this.env._t('Offline'),
                            body: this.env._t('Unable to save changes.'),
                        });
                    } else {
                        throw error;
                    }
                }
            }
        }

    Registries.Component.extend(ClientListScreen, BiClientListScreen);
    return ClientListScreen;
});
