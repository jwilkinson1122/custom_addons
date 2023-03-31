# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PodiatryDeviceModelLine(models.Model):
    _name = 'podiatry.device.model.line'
    _description = 'Line of the device'
    _order = 'name asc'

    name = fields.Char('Make', required=True)
    image_128 = fields.Image("Logo", max_width=128, max_height=128)
    model_count = fields.Integer(compute="_compute_model_count", string="", store=True)
    model_ids = fields.One2many('podiatry.device.model', 'line_id')

    @api.depends('model_ids')
    def _compute_model_count(self):
        Model = self.env['podiatry.device.model']
        for record in self:
            record.model_count = Model.search_count([('line_id', '=', record.id)])

    def action_line_model(self):
        self.ensure_one()
        view = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'podiatry.device.model',
            'name': 'Models',
            'context': {'search_default_line_id': self.id, 'default_line_id': self.id}
        }

        return view
