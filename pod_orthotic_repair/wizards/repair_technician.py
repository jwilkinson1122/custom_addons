# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class RepairTechnician(models.TransientModel):
    """Repair Technician"""
    _name = 'repair.technician'
    _description = __doc__

    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order', string="Repair Order")
    team_id = fields.Many2one('repair.team', string="Team", required=True)
    team_member_ids = fields.Many2many(related="team_id.team_member_ids")
    technician_id = fields.Many2one('res.users', string="Technician", required=True,
                                    domain="[('id', 'in', team_member_ids)]")

    @api.model
    def default_get(self, fields):
        res = super(RepairTechnician, self).default_get(fields)
        res['orthotic_repair_order_id'] = self._context.get('active_id')
        return res

    def repair_technician_details(self):
        record = self._context.get('active_id')
        repair_data = self.env['orthotic.repair.order'].browse(record)
        repair_data.write({
            'team_id': self.team_id.id,
            'technician_id': self.technician_id.id,
            'stages': 'assign_to_technician',
        })
