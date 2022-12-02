odoo.define('podiatry.ClientListScreen', function (require) {
    'use strict';

    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { useState } = owl.hooks;

    const PodiatryClientListScreen = ClientListScreen =>
        class extends ClientListScreen {
            get prescription_count() {
                self = this;
                if (this.state.selectedClient)
                    return self.env.pos.podiatry.all_orders.filter(function (el) { return el.customer[0] === self.state.selectedClient.id }).length
                else
                    return 0
            }

            prescription_count_click(data) {
                var podiatry_orders = this.env.pos.podiatry.all_orders.filter(function (el) { return el.customer[0] === data.id })
                this.trigger('close-temp-screen');
                this.showScreen('PrescriptionListScreenWidget', { all_orders: podiatry_orders });
            }
            /**
             * @override
             */
            async saveChanges(event) {
                try {
                    let partnerId = await this.rpc({
                        model: 'res.partner',
                        method: 'create_partner_from_ui',
                        args: [event.detail.processedChanges, event.detail.extraprocessedChanges],
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

    Registries.Component.extend(ClientListScreen, PodiatryClientListScreen);
    return ClientListScreen;
});
