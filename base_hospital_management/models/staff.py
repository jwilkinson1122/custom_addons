# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Staff(models.Model):
    _name = 'hospital.staffs'
    _description = 'Staff'
    department_id = fields.Many2one('res.partner', string="Department",
                                    )
    staff_id = fields.Many2many('res.partner', string="Staff",
                                readonly='1')
    _rec_name = 'department_id'

    @api.onchange('department_id')
    def _onchange_department(self):
        """staffs taking basis of department"""
        for rec in self:
            rec.staff_id = rec.env['res.partner'].search([('department_id', '=',
                                                       rec.department_id.name)])
