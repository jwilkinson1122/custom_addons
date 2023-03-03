odoo.define('pod_dev.ClientDetailsEdit', function (require) {
	'use strict';

	const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
	const Registries = require('point_of_sale.Registries');
	const { useState, useRef } = owl.hooks;

	const BiClientDetailsEdit = ClientDetailsEdit =>
		class extends ClientDetailsEdit {
			/**
			 * @override
			 */
			constructor() {
				super(...arguments);
				this.new_state = useState({ value: [], exist_value: [] });
				this.partnerData();
				this.intFields = ['country_id', 'state_id', 'property_product_pricelist'];
				const partner = this.props.partner;
				this.extra_info = {
					'country_id': partner.country_id && partner.country_id[0],
					'state_id': partner.state_id && partner.state_id[0],
				};
			}
			async partnerData() {
				var self = this;
				var not_exist = []
				var data1 = []
				const info_data = await this.rpc({
					model: 'res.partner.info',
					method: 'search_read',
					fields: [],
					domain: [['partner_id', '=', self.props.partner.id]]
				});

				_.each(self.env.pos.custom_field, function (field) {
					data1.push(field)
				})
				_.each(info_data, function (data) {
					data1 = data1.filter(function (item) {
						return item.name != data.name;
					});
				})
				self.new_state.exist_value = data1
				self.new_state.value = info_data;
			}
			extracaptureChange(event) {
				this.extra_info[event.target.name] = event.target.value;
			}
			saveChanges() {
				let self = this;
				let processedChanges = {};
				for (let [key, value] of Object.entries(this.changes)) {
					if (this.intFields.includes(key)) {
						processedChanges[key] = parseInt(value) || false;
					} else {
						processedChanges[key] = value;
					}
				}
				if (processedChanges.name === '') {
					return this.showPopup('ErrorPopup', {
						title: _t('A Customer Name Is Required'),
					});
				}
				processedChanges.id = this.props.partner.id || false;

				let extraprocessedChanges = {};
				for (let [key, value] of Object.entries(this.extra_info)) {
					if (this.intFields.includes(key)) {
						extraprocessedChanges[key] = parseInt(value) || false;
					} else {
						extraprocessedChanges[key] = value;
					}
				}
				if ((!this.props.partner.name && !extraprocessedChanges.name) ||
					extraprocessedChanges.name === '') {
					return this.showPopup('ErrorPopup', {
						title: _t('A Customer Name Is Required'),
					});
				}
				extraprocessedChanges.id = this.props.partner.id || false;

				this.trigger('save-changes', {
					processedChanges,
					extraprocessedChanges
				});
			}
		};


	Registries.Component.extend(ClientDetailsEdit, BiClientDetailsEdit);

	return ClientDetailsEdit;
});
