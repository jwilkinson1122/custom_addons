import logging

from dateutil.relativedelta import relativedelta
from odoo import _, models, fields, api
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class PodiatryPatient(models.Model):
    _name = "pod.patient"
    _description = "Podiatry Patient"
    _inherit = ["pod.abstract", "mail.thread", "mail.activity.mixin"]
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one("res.partner", required=True, ondelete="restrict")
    
    is_patient = fields.Boolean()

    pod_account_id = fields.Many2one(
        string="Account",
        comodel_name="res.partner",
        domain=[("is_company", "=", True)],
    )

    pod_location_id = fields.Many2one(
        string="Location",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )

    pod_practitioner_id = fields.Many2one(
        string="Primary Practitioner",
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
    )

    other_pod_practitioner_ids = fields.Many2many(
        string="Other Practitioners",
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
    )
    
    relation_label = fields.Char('Partner relation label', translate=True, default='Responsible:', readonly=True)
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
    
    # patient_pod_ids = fields.One2many("pod.pod.order", inverse_name="pod_patient_id")
    # patient_pod_count = fields.Integer(compute="_compute_patient_pod_count")
            
    # @api.depends("patient_pod_ids")
    # def _compute_patient_pod_count(self):
    #     for rec in self:
    #         rec.patient_pod_count = len(rec.patient_pod_ids.ids)


    # def action_view_patient_prescriptions(self):
    #     self.ensure_one()
    #     result = self.env["ir.actions.act_window"]._for_xml_id("pod_order_mgmt.action_pod_pod_orders")
    #     result["context"] = {"default_pod_patient_id": self.id}
    #     result["domain"] = "[('pod_patient_id', '=', " + str(self.id) + ")]"
    #     if len(self.patient_pod_ids) == 1:
    #         res = self.env.ref("pod_order_mgmt.view_pod_pod_order_form", False)  # Ensure the XML ID is correct
    #         result["views"] = [(res and res.id or False, "form")]
    #         result["res_id"] = self.patient_pod_ids.ids[0]   
    #     return result

    shoe_type = fields.Selection([
        ('dress', 'Dress'), 
        ('casual', 'Casual'), 
        ('athletic', 'Athletic'), 
        ('other', 'Other')
        ], string='Shoe Type')
    
    notes = fields.Text(string="Notes")

    gender = fields.Selection([
        ("male", "Male"), 
        ("female", "Female"), 
        ("other", "Other")], string='Gender') 
     
    birth_date = fields.Date(string="Birth date")  
    
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
            
            
    patient_flag_ids = fields.One2many("pod.flag", inverse_name="pod_patient_id")
    patient_flag_count = fields.Integer(compute="_compute_patient_flag_count")
            
    @api.depends("patient_flag_ids")
    def _compute_patient_flag_count(self):
        for rec in self:
            rec.patient_flag_count = len(rec.patient_flag_ids.ids)

    def action_view_patient_flags(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id("pod_contacts.pod_flag_action")
        result["context"] = {"default_pod_patient_id": self.id}
        result["domain"] = "[('pod_patient_id', '=', " + str(self.id) + ")]"
        if len(self.patient_flag_ids) == 1:
            res = self.env.ref("pod.flag.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.patient_flag_ids.id
        return result

    @api.model
    def _get_pod_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].sudo().next_by_code("pod.patient")
            or "New"
        )
        
    @api.model_create_multi
    def create(self, vals_list):
        records = super(PodiatryPatient, self).create(vals_list)
        for record in records:
            record.apply_practitioner_logic()
        return records
    
    
    def apply_practitioner_logic(self):
        """Automatically assign a practitioner based on the parent_id."""
        if self.parent_id:
            # Searching for practitioners whose parent_id matches the selected account
            practitioners = self.env['res.partner'].search([
                ('is_practitioner', '=', True), 
                ('parent_id', '=', self.parent_id.id)
            ])
            # If any practitioners are found, assign the first one to the patient
            if practitioners:
                self.pod_practitioner_id = practitioners[0]


    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        """Update the domain of pod_practitioner_id based on the selected parent_id."""
        self.apply_practitioner_logic()
        if self.parent_id:
            # Set the domain to include only practitioners whose parent_id matches the selected account
            return {
                'domain': {
                    'pod_practitioner_id': [('is_practitioner', '=', True), ('parent_id', '=', self.parent_id.id)]
                }
            }
        else:
            # If no account is selected, revert to the initial domain
            return {
                'domain': {
                    'pod_practitioner_id': [('is_practitioner', '=', True)]
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
        
    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Podiatrys',
            'res_model': 'pod.pod.order',
            'domain': [('pod_patient_id', '=', self.id)],
            'context': {'default_pod_patient_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
        
    def unlink(self):
        # Trying to delete the records in the current recordset
        try:
            return super(PodiatryPatient, self).unlink()
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