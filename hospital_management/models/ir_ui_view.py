from odoo import api, fields, models, _


class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('catalog', "Catalog")])


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('catalog', "Catalog")], ondelete={'catalog': 'cascade'})


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_catalog_data(self, domain, catalog_field):
        records = self.search(domain)
        result_dict = {}
        for record in records:
            for rec in record[catalog_field]:
                if rec.id not in result_dict:
                    result_dict[rec.id] = {
                        'name': rec.display_name,
                        'children': [],
                        'model': rec._name
                    }
        result_dict[rec.id]['children'].append({
            'name': record.display_name,
            'id': record.id,
        })
        return result_dict
