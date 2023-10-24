# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools
from datetime import timedelta
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
     
class Partner(models.Model):
    _inherit = "res.partner"
    
    # practice_id = fields.Many2one('res.partner', string="Practice", domain=[('is_practice', '=', True)])
    # practitioner_id = fields.Many2one('res.partner', string="Practitioner", domain=[('is_practitioner', '=', True)])
    
    practice_id = fields.Many2one(
        'res.partner', 
        required=True, 
        index=True, 
        domain=[('is_company','=',True)], 
        string="Practice"
        )
    
    practitioner_id = fields.Many2one(
        'res.partner', 
        required=True, 
        index=True, 
        domain=[('is_practitioner','=',True)], 
        string="Practitioner"
        )
    
    patient_id = fields.Many2one(
        "pod.patient", 
        string="Patient",
        required=True, 
        index=True, 
        states={"draft": [("readonly", False)], "done": [("readonly", True)]}
    )
    
    practice_prescription_orders = fields.One2many(
        "pod.prescription.order",
        "practice_id",
        domain=[("active", "=", True)],
    )
    
    practitioner_prescription_orders = fields.One2many(
        "pod.prescription.order",
        "practitioner_id",
        domain=[("active", "=", True)],
    )
    
    prescription_order_lines = fields.One2many(
        'pod.prescription.order.line', 
        'prescription_order_id', 
        'Prescription Line')

    prescription_order_count = fields.Integer(compute='_compute_prescription_order_count')

    @api.depends('practice_prescription_orders', 'practitioner_prescription_orders')
    def _compute_prescription_order_count(self):
        for record in self:
            record.prescription_order_count = len(record.practice_prescription_orders) + len(record.practitioner_prescription_orders)

    def action_view_prescription_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'pod.prescription.order',
            'domain': ['|', ('practice_id', '=', self.id), ('practitioner_id', '=', self.id)],
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }

    def _get_last_prescription(self, prescription_type):
        prescriptions = self.practice_prescription_orders if prescription_type == 'practice' else self.practitioner_prescription_orders
        if not prescriptions:
            raise ValidationError(_("No prescriptions can be found for this %s") % prescription_type)
        return prescriptions[0]
    

    def action_open_practice_prescriptions(self):
        self.ensure_one()
        return {
            'name': _('Prescriptions'),
            'type': 'ir.actions.act_window',
            'res_model': 'pod.prescription.order',
            'view_mode': 'kanban,tree,form',
            'domain': [('practice_id', '=', self.id)],
            'context': {'default_practice_id': self.id},
            'target': 'current',
        }

    def action_open_practitioner_prescriptions(self):
        self.ensure_one()
        return {
            'name': _('Prescriptions'),
            'type': 'ir.actions.act_window',
            'res_model': 'pod.prescription.order',
            'view_mode': 'kanban,tree,form',
            'domain': [('practitioner_id', '=', self.id)],
            'context': {'default_practitioner_id': self.id},
            'target': 'current',
        }