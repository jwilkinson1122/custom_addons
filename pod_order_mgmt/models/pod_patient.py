import base64
from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class Patient(models.Model):
    _inherit = "pod.patient"
    
   
    notes = fields.Text(string="Notes")

    prescription_order_ids = fields.One2many(
        "pod.prescription.order",
        "patient_id",
        string="Patients Prescriptions",
        domain=[("active", "=", True)],
    )
    
    prescription_order_lines = fields.One2many(
        'pod.prescription.order.line', 
        'prescription_order_id', 
        'Prescription Line')

    prescription_count = fields.Integer(compute="_compute_prescription_count")
    
    @api.depends("prescription_order_ids")
    def _compute_prescription_count(self):
        for record in self:
            record.prescription_count = len(record.prescription_order_ids)

    def action_view_prescription_order_ids(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("pod_order_mgmt.action_pod_prescription_orders")
        action["domain"] = [("patient_id", "=", self.id)]
        return action

    def _get_last_prescription(self):
        if not self.prescription_order_ids:
            raise ValidationError(_("No prescriptions can be found for this patient"))
        return self.prescription_order_ids[0]


    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'pod.prescription.order',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
