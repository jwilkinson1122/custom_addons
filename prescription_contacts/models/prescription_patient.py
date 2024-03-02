import logging

from dateutil.relativedelta import relativedelta
from odoo import _, models, fields, api
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class PrescriptionPatient(models.Model):
    _name = "prescription.patient"
    _description = "Prescription Patient"
    _inherit = ["prescription.abstract", "mail.thread", "mail.activity.mixin"]
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one("res.partner", required=True, ondelete="restrict")
    is_patient = fields.Boolean()
    location_id = fields.Many2one(
        string="Account",
        comodel_name="res.partner",
        domain=[("is_company", "=", True)],
    )

    location_id = fields.Many2one(
        string="Practitioner",
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
    )

    other_location_ids = fields.Many2many(
        string="Other Practitioners",
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
    )
    
    partner_relation_label = fields.Char('Partner relation label', translate=True, default='Responsible:', readonly=True)
    
    
    user_id = fields.Many2one('res.users', 'Created By:', default=lambda self: self.env.user.id)
    barcode = fields.Char(string='Barcode')
    attachment_ids = fields.Many2many('ir.attachment', 'patient_ir_attachments_rel',
                                      'manager_id', 'attachment_id', string="Attachments",
                                      help="Patient Image / File Attachments")
    
    photo = fields.Binary(string="Picture")
    image1 = fields.Binary("Right photo")
    image2 = fields.Binary("Left photo")
    left_obj_model = fields.Binary("Left Obj")
    left_obj_file_name = fields.Char(string="Left Obj File Name")
    right_obj_model = fields.Binary("Right Obj")
    right_obj_file_name = fields.Char(string="Right Obj File Name")
    pt_height = fields.Integer("Height", store="True", copy="True")
    pt_weight = fields.Float("Weight", store="True", copy="True")
    pt_age = fields.Integer("Age", store="True", copy="True", compute="_compute_age")
    shoe_size = fields.Float("Shoe Size", store="True", copy="True")
    shoe_type = fields.Selection([('dress', 'Dress'), ('casual', 'Casual'), ('athletic', 'Athletic'), ('other', 'Other')], string='Shoe Type')
    shoe_width = fields.Selection([("wide", "Wide"), ("xwide", "Extra Wide"), ("narrow", "Narrow")]) 
    notes = fields.Text(string="Notes")
    gender = fields.Selection([("male", "Male"), ("female", "Female"), ("other", "Other")])  
    birth_date = fields.Date(string="DOB")  
    patient_age = fields.Integer(compute="_compute_age")

    @api.depends("birth_date")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.birth_date:
                age = relativedelta(
                    fields.Date.today(), record.birth_date
                ).years
            record.patient_age = age

    # Flags           
    patient_flag_ids = fields.One2many("prescription.flag", inverse_name="patient_id")
    patient_flag_count = fields.Integer(compute="_compute_patient_flag_count")
            
    @api.depends("patient_flag_ids")
    def _compute_patient_flag_count(self):
        for rec in self:
            rec.patient_flag_count = len(rec.patient_flag_ids.ids)

    def action_view_patient_flags(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id("prescription_contacts.prescription_flag_action")
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = "[('patient_id', '=', " + str(self.id) + ")]"
        if len(self.patient_flag_ids) == 1:
            res = self.env.ref("prescription.flag.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.patient_flag_ids.id
        return result

    # This Fuction is used for the Cancel Button =========================== item_cancel
    def btn_customer_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def btn_customer_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'

    def btn_view_prescription(self):
        pass
    def btn_view_prescription(self):
        pass


    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].sudo().next_by_code("prescription.patient")
            or "/"
        )
        
    @api.model_create_multi
    def create(self, vals_list):
        records = super(PrescriptionPatient, self).create(vals_list)
        for record in records:
            record.apply_practitioner_logic()
        return records
    
    def apply_practitioner_logic(self):
        """Automatically assign a practitioner based on the parent_id."""
        if self.parent_id:
            # Searching for practitioners whose parent_id matches the selected practice
            practitioners = self.env['res.partner'].search([
                ('is_practitioner', '=', True), 
                ('parent_id', '=', self.parent_id.id)
            ])
            # If any practitioners are found, assign the first one to the patient
            if practitioners:
                self.location_id = practitioners[0]

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        """Update the domain of location_id based on the selected parent_id."""
        self.apply_practitioner_logic()
        if self.parent_id:
            # Set the domain to include only practitioners whose parent_id matches the selected practice
            return {
                'domain': {
                    'location_id': [('is_practitioner', '=', True), ('parent_id', '=', self.parent_id.id)]
                }
            }
        else:
            # If no practice is selected, revert to the initial domain
            return {
                'domain': {
                    'location_id': [('is_practitioner', '=', True)]
                }
            }

            
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
        

    
        
    def unlink(self):
        # Trying to delete the records in the current recordset
        try:
            return super(PrescriptionPatient, self).unlink()
        except Exception as e:
            _logger.error(f"An error occurred while trying to delete the patient records: {e}")

    @api.model
    def delete_patient_by_partner_id(self, partner_id):
        # Searching for the patient record with the specified partner_id
        patient_to_delete = self.search([('partner_id', '=', partner_id)], limit=1)
        
        if patient_to_delete:
            try:
                # Trying to delete the found record
                patient_to_delete.unlink()
                return _("Patient record deleted successfully.")
            except Exception as e:
                # Logging the error and raising a user-friendly error message
                _logger.error(f"An error occurred while trying to delete the patient record: {e}")
                raise UserError(_("An error occurred while trying to delete the patient record."))
        else:
            # No record found for the specified partner_id
            return _("No patient record found for the specified partner_id.")