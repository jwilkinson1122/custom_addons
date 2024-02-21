# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models, tools
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.osv import expression




_logger = logging.getLogger(__name__)

class PrescriptionPatient(models.Model):
    _inherit = 'prescription.patient'


    prescription_ids = fields.One2many(
        "prescription.order",
        "patient_id",
        string="Prescriptions",
        # domain=[("active", "=", True)],
    )
    
    # prescription_lines = fields.One2many(
    #     'prescription.order.line', 
    #     'order_id', 
    #     'Prescription Line')

    prescription_count = fields.Integer(
        string="Prescription Count",
        compute="_compute_prescription_count",
        store=True,
    )

    @api.depends('prescription_ids')
    def _compute_prescription_count(self):
        for record in self:
            record.prescription_count = len(record.prescription_ids)


    def _get_last_prescription(self):
        prescriptions = self.prescription_ids
        if not prescriptions:
            raise ValidationError(_("No prescriptions can be found for this patient"))
        return prescriptions[0]
    

    def action_open_patient_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'prescription.order',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
    
  
      # Flags           
    # patient_prescription_ids = fields.One2many("prescription.order", inverse_name="patient_id")
    # patient_prescription_count = fields.Integer(compute="_compute_patient_prescription_count")
            
    # @api.depends("patient_prescription_ids")
    # def _compute_patient_prescription_count(self):
    #     for rec in self:
    #         rec.patient_prescription_count = len(rec.patient_prescription_ids.ids)

    # def action_view_patient_prescriptions(self):
    #     self.ensure_one()
    #     result = self.env["ir.actions.act_window"]._for_xml_id("pod_prescription.patient_prescription_action")
    #     result["context"] = {"default_patient_id": self.id}
    #     result["domain"] = "[('patient_id', '=', " + str(self.id) + ")]"
    #     if len(self.patient_prescription_ids) == 1:
    #         res = self.env.ref("prescription.order.form", False)
    #         result["views"] = [(res and res.id or False, "form")]
    #         result["res_id"] = self.patient_prescription_ids.id
    #     return result
