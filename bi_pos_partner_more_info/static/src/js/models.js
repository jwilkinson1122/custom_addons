odoo.define('bi_pos_partner_more_info.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    models.load_fields('res.partner',['info_ids'])

	models.load_models({
		model: 'res.partner.info',
		fields: ['name','info_name','partner_id','field_id'],
		domain: null,
		loaded: function(self, info) {
			self.more_info = info;
		},
	});
	models.load_models({
		model: 'custom.field',
		fields: [],
		domain: function(self) {
			return [
				['id', 'in', self.config.show_custom_field]
			];
		},
		loaded: function(self, field) {
			self.custom_field = field;
		},
	});
});
