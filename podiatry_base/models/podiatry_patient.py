from odoo import api, fields, models


class PodiatryPatient(models.Model):
    # FHIR Entity: Patient (http://hl7.org/fhir/patient.html)
    _name = "podiatry.patient"
    _description = "Podiatry Patient"
    _inherit = ["podiatry.abstract", "mail.thread", "mail.activity.mixin"]
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        "res.partner", required=True, ondelete="restrict"
    )

    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")]
    )  
    
    birth_date = fields.Date(string="Birth date")   

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].sudo().next_by_code("podiatry.patient")
            or "ID"
        )
        
    prescription_count = fields.Integer(string='Prescription Count', compute='_compute_prescription_count')
    prescription_id = fields.Many2one('sale.order', 'patient_id', required=True, ondelete="cascade")
    # prescription_id = fields.One2many(comodel_name='podiatry.prescription', inverse_name='patient_id', string="Prescriptions")

    prescription_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', readonly=True)
    
 
    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['sale.order'].search_count(
                [('patient_id', '=', rec.id)])
            rec.prescription_count = prescription_count
            
        attachment_ids = fields.Many2many('ir.attachment', 'patient_ir_attachments_rel',
                                      'manager_id', 'attachment_id', string="Attachments", help="Patient Image / File Attachments")

    image1 = fields.Binary("Right photo")
    image2 = fields.Binary("Left photo")

    left_obj_model = fields.Binary("Left Obj")
    left_obj_file_name = fields.Char(string="Left Obj File Name")
    right_obj_model = fields.Binary("Right Obj")
    right_obj_file_name = fields.Char(string="Right Obj File Name")

    def open_parent(self):
        """Utility method used to add an "Open Parent" button in partner
        views"""
        self.ensure_one()
        address_form_id = self.env.ref("base.view_partner_address_form").id
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "form",
            "views": [(address_form_id, "form")],
            "res_id": self.parent_id.id,
            "target": "new",
            "flags": {"form": {"action_buttons": True}},
        }
        
    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'sale.order',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
