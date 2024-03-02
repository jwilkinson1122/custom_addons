# -*- coding: utf-8 -*-


from odoo import api, fields, models


class PrescriptionTypeModelLine(models.Model):
    _name = 'prescription.type.model.line'
    _description = 'Line of the prescription type'
    _order = 'name asc'

    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True)
    image_128 = fields.Image("Logo", max_width=128, max_height=128)
    model_count = fields.Integer(compute="_compute_model_count", string="", store=True)
    model_ids = fields.One2many('prescription.type.model', 'line_id')

    @api.depends('model_ids')
    def _compute_model_count(self):
        model_data = self.env['prescription.type.model']._read_group([
            ('line_id', 'in', self.ids),
        ], ['line_id'], ['__count'])
        models_line = {line.id: count for line, count in model_data}

        for record in self:
            record.model_count = models_line.get(record.id, 0)

    def action_line_model(self):
        self.ensure_one()
        view = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'prescription.type.model',
            'name': 'Types',
            'context': {'search_default_line_id': self.id, 'default_line_id': self.id}
        }

        return view
