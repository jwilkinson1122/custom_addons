

from odoo import api, fields, models


class PodiatryPatient(models.Model):
    _name = "podiatry.patient"
    _description = "Podiatry Patient"
    _inherit = ["podiatry.abstract", "mail.thread", "mail.activity.mixin"]
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        "res.partner", required=True, ondelete="cascade")
    primary_doctor_id = fields.Many2one('res.partner', domain=[(
        'is_practitioner', '=', True)], string="Primary Doctor", )
    patient_height = fields.Char(string="Height")
    patient_weight = fields.Char(string="Weight")
    diagnosis = fields.Char(string='Diagnosis')
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")])
    photo = fields.Binary(string="Picture")
    birth_date = fields.Date(string="Birth date")
    shoe_size = fields.Float('Shoe Size')
    shoe_width = fields.Selection(
        [('narrow', 'Narrow'), ('wide', 'Wide'), ('xwide', 'Extra Wide')], string='Shoe Width')
    shoe_type = fields.Selection([('dress', 'Dress'), ('casual', 'Casual'), (
        'athletic', 'Athletic'), ('other', 'Other')], string='Shoe Type')
    other_shoe_type = fields.Char('Other Shoe Type')
    right_photo = fields.Image("Right Photo")
    left_photo = fields.Image("Left Photo")
    left_obj_model = fields.Binary("Left Obj")
    left_obj_file_name = fields.Char(string="Left Obj File Name")
    right_obj_model = fields.Binary("Right Obj")
    right_obj_file_name = fields.Char(string="Right Obj File Name")

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("podiatry.patient") or "PID"

    @api.model
    def create(self, vals):
        vals_upd = vals.copy()
        return super(PodiatryPatient, self).create(vals_upd)

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

    # def action_open_prescriptions(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Prescriptions',
    #         'res_model': 'podiatry.prescription.administration',
    #         'domain': [('patient_id', '=', self.id)],
    #         'context': {'default_patient_id': self.id},
    #         'view_mode': 'tree,form',
    #         'target': 'current',
    #     }
