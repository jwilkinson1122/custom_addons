# -*- coding: utf-8 -*-


from odoo import _, api, fields, models
from odoo.osv import expression


SHELL_TYPES = [
    ('diesel', 'Diesel'),
    ('gasoline', 'Gasoline'),
    ('full_hybrid', 'Full Hybrid'),
    ('plug_in_hybrid_diesel', 'Plug-in Hybrid Diesel'),
    ('plug_in_hybrid_gasoline', 'Plug-in Hybrid Gasoline'),
    ('cng', 'CNG'),
    ('lpg', 'LPG'),
    ('hydrogen', 'Hydrogen'),
    ('electric', 'Electric'),
]

ARCH_HEIGHT = [
    ('very_high', 'Very High'),
    ('high', 'High'),
    ('standard', 'Standard'),
    ('low', 'Low'),
]


class PrescriptionTypeModel(models.Model):
    _name = 'prescription.type.model'
    _inherit = ['avatar.mixin']
    _description = 'Model of a prescription'
    _order = 'name asc'

    name = fields.Char('Model name', required=True)
    line_id = fields.Many2one('prescription.type.model.line', 'Line', required=True)
    category_id = fields.Many2one('prescription.type.model.category', 'Category')
    vendors = fields.Many2many('res.partner', 'prescription_type_model_vendors', 'model_id', 'partner_id', string='Vendors')
    image_128 = fields.Image(related='line_id.image_128', readonly=True)
    active = fields.Boolean(default=True)
    prescription_type = fields.Selection([
        ('custom', 'Custom'), 
        ('otc', 'OTC'),
        ('brace', 'Brace'),
        ('blanks', 'Blanks'),
        ], default='custom', required=True, string='Prescription Type')

    prescription_type_count = fields.Integer(compute='_compute_prescription_type_count', search='_search_prescription_type_count')
    model_year = fields.Integer()
    color = fields.Char()
    pairs = fields.Integer(string='Pairs to Make')
    qty = fields.Integer(string='QTY Number')
    trailer_hook = fields.Boolean(default=False, string='Trailer Hitch')
    default_co2 = fields.Float('CO2 Emissions')
    co2_standard = fields.Char()
    
    
    default_shell_type = fields.Selection(SHELL_TYPES, 'Shell Type', default='electric')
    default_arch_height = fields.Selection(ARCH_HEIGHT, 'Arch Height', default='standard')

    power = fields.Integer('Power')
    horsepower = fields.Integer()
    horsepower_tax = fields.Float('Horsepower Taxation')


    electric_assistance = fields.Boolean(default=False)


    # low_profile_shoes = fields.Selection([
    #     ('custom', 'Custom'), 
    #     ('otc', 'OTC'),
    #     ('brace', 'Brace'),
    #     ('blanks', 'Blanks'),
    #     ], default='custom', required=True, string='Prescription Type')


    prescription_properties_definition = fields.PropertiesDefinition('Prescription Properties')

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if operator != 'ilike' or (name or '').strip():
            name_domain = ['|', ('name', 'ilike', name), ('line_id.name', 'ilike', name)]
            domain = expression.AND([name_domain, domain])
        return self._search(domain, limit=limit, order=order)

    @api.depends('line_id')
    def _compute_display_name(self):
        for record in self:
            name = record.name
            if record.line_id.name:
                name = f"{record.line_id.name}/{name}"
            record.display_name = name

    def _compute_prescription_type_count(self):
        group = self.env['prescription.type']._read_group(
            [('model_id', 'in', self.ids)], ['model_id'], aggregates=['__count'],
        )
        count_by_model = {model.id: count for model, count in group}
        for model in self:
            model.prescription_type_count = count_by_model.get(model.id, 0)

    @api.model
    def _search_prescription_type_count(self, operator, value):
        if operator not in ['=', '!=', '<', '>'] or not isinstance(value, int):
            raise NotImplementedError(_('Operation not supported.'))
        prescription_models = self.env['prescription.type.model'].search([])
        if operator == '=':
            prescription_models = prescription_models.filtered(lambda m: m.prescription_type_count == value)
        elif operator == '!=':
            prescription_models = prescription_models.filtered(lambda m: m.prescription_type_count != value)
        elif operator == '<':
            prescription_models = prescription_models.filtered(lambda m: m.prescription_type_count < value)
        elif operator == '>':
            prescription_models = prescription_models.filtered(lambda m: m.prescription_type_count > value)
        return [('id', 'in', prescription_models.ids)]

    def action_model_prescription_type(self):
        self.ensure_one()
        view = {
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'prescription.type',
            'name': _('Prescription'),
            'context': {'search_default_model_id': self.id, 'default_model_id': self.id}
        }

        return view
