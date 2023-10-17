import logging

from dateutil.relativedelta import relativedelta
from odoo import _, models, fields, api
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class PodiatryPatient(models.Model):
    # FHIR Entity: Patient (http://hl7.org/fhir/patient.html)
    _name = "pod.patient"
    _description = "Podiatry Patient"
    _inherit = ["pod.abstract", "mail.thread", "mail.activity.mixin"]
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        "res.partner", required=True, ondelete="restrict"
    )
    
    # practice_id = fields.Many2one(
    #     'res.partner', 
    #     required=True, 
    #     index=True, 
    #     domain=[('is_company','=',True)], 
    #     string="Practice"
    #     )

    practitioner_id = fields.Many2one(
        string="Primary Practitioner",
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
    )

    other_practitioner_ids = fields.Many2many(
        string="Other Practitioners",
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
    )
    
    partner_relation_label = fields.Char('Partner relation label', translate=True, default='Responsible:', readonly=True)
    
    # patient_prescription_ids = fields.One2many("pod.prescription.order", inverse_name="patient_id")
    # patient_prescription_count = fields.Integer(compute="_compute_patient_prescription_count")
            
    # @api.depends("patient_prescription_ids")
    # def _compute_patient_prescription_count(self):
    #     for rec in self:
    #         rec.patient_prescription_count = len(rec.patient_prescription_ids.ids)


    # def action_view_patient_prescriptions(self):
    #     self.ensure_one()
    #     result = self.env["ir.actions.act_window"]._for_xml_id("pod_order_mgmt.action_pod_prescription_orders")
    #     result["context"] = {"default_patient_id": self.id}
    #     result["domain"] = "[('patient_id', '=', " + str(self.id) + ")]"
    #     if len(self.patient_prescription_ids) == 1:
    #         res = self.env.ref("pod_order_mgmt.view_pod_prescription_order_form", False)  # Ensure the XML ID is correct
    #         result["views"] = [(res and res.id or False, "form")]
    #         result["res_id"] = self.patient_prescription_ids.ids[0]   
    #     return result

    gender = fields.Selection([("male", "Male"), ("female", "Female"), ("other", "Other")])  
    birth_date = fields.Date(string="Birth date")  # FHIR Field: birthDate
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
            
            
    patient_flag_ids = fields.One2many("pod.flag", inverse_name="patient_id")
    patient_flag_count = fields.Integer(compute="_compute_patient_flag_count")
            
    @api.depends("patient_flag_ids")
    def _compute_patient_flag_count(self):
        for rec in self:
            rec.patient_flag_count = len(rec.patient_flag_ids.ids)

    def action_view_patient_flags(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id("pod_base.pod_flag_action")
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = "[('patient_id', '=', " + str(self.id) + ")]"
        if len(self.patient_flag_ids) == 1:
            res = self.env.ref("pod.flag.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.patient_flag_ids.id
        return result

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].sudo().next_by_code("pod.patient")
            or "/"
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
            # Searching for practitioners whose parent_id matches the selected practice
            practitioners = self.env['res.partner'].search([
                ('is_practitioner', '=', True), 
                ('parent_id', '=', self.parent_id.id)
            ])
            # If any practitioners are found, assign the first one to the patient
            if practitioners:
                self.practitioner_id = practitioners[0]


    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        """Update the domain of practitioner_id based on the selected parent_id."""
        self.apply_practitioner_logic()
        if self.parent_id:
            # Set the domain to include only practitioners whose parent_id matches the selected practice
            return {
                'domain': {
                    'practitioner_id': [('is_practitioner', '=', True), ('parent_id', '=', self.parent_id.id)]
                }
            }
        else:
            # If no practice is selected, revert to the initial domain
            return {
                'domain': {
                    'practitioner_id': [('is_practitioner', '=', True)]
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
            'name': 'Prescriptions',
            'res_model': 'pod.prescription.order',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
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