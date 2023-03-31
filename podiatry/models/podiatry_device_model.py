# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


DEVICE_TYPES = [
    ('custom', 'Custom'),
    ('otc_child', 'OTC Child Device'),
    ('otc_adult', 'OTC Adult Device'),
    ('polypropylene', 'Polypropylene Device'),
    ('brace', 'Brace'),
]

class PodiatryDeviceModel(models.Model):
    _name = 'podiatry.device.model'
    _description = 'Model of a device'
    _order = 'name asc'

    name = fields.Char('Model name', required=True)
    line_id = fields.Many2one('podiatry.device.model.line', 'Manufacturer', required=True, help='Manufacturer of the device')
    category_id = fields.Many2one('podiatry.device.model.category', 'Category')
    vendors = fields.Many2many('res.partner', 'podiatry_device_model_vendors', 'model_id', 'partner_id', string='Vendors')
    image_128 = fields.Image(related='line_id.image_128', readonly=True)
    active = fields.Boolean(default=True)
    device_type = fields.Selection([('device', 'Device'), ('other', 'Other')], default='device', required=True)
    arch_height = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic')], 'Arch Height', help='Arch Height Used by the device')
    arch_height = fields.Selection(
        [('very_high', 'Very High'), 
         ('high', 'High'),
         ('standard', 'Standard'),
         ('low', 'Low'),
         ], 'Arch Height', default='standard', help='Arch Height of the device')
    device_count = fields.Integer(compute='_compute_device_count')
    color = fields.Char()
    pairs = fields.Integer(string='Seats Number')
    default_device_type = fields.Selection(DEVICE_TYPES, 'Device Type', default='diesel')
    patient_weight = fields.Integer()

    @api.depends('name', 'line_id')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.line_id.name:
                name = record.line_id.name + '/' + name
            res.append((record.id, name))
        return res

    def _compute_device_count(self):
        group = self.env['podiatry.device'].read_group(
            [('model_id', 'in', self.ids)], ['id', 'model_id'], groupby='model_id', lazy=False,
        )
        count_by_model = {entry['model_id'][0]: entry['__count'] for entry in group}
        for model in self:
            model.device_count = count_by_model.get(model.id, 0)

    def action_model_device(self):
        self.ensure_one()
        view = {
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'podiatry.device',
            'name': _('Devices'),
            'context': {'search_default_model_id': self.id, 'default_model_id': self.id}
        }

        return view
