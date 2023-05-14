from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models,_

class InheritedResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_practitioner = fields.Boolean(string="Practitioner")
    is_practice = fields.Boolean('Practice')
    is_patient = fields.Boolean(string='Patient')
    
    # force "active_test" domain to bypass _search() override
    child_ids = fields.One2many(domain=[("active", "=", True), ("is_practice", "=", False), ("is_company", "=", False)])
    practice_id = fields.Many2one('res.partner',domain=[('is_practice','=',True)])
    practice_ids = fields.One2many("res.partner", "parent_id", string="Practices", domain=[("active", "=", True), ("is_practice", "=", True), ("is_company", "=", True)])
    practitioner_ids = fields.One2many("pod.practitioner", "partner_id", string="Practitioners", domain=[("active", "=", True), ("is_practitioner", "=", True), ("is_company", "=", False)])
    patient_ids = fields.One2many("pod.patient", "partner_id", string="Patients", domain=[("active", "=", True), ("is_patient", "=", True), ("is_company", "=", False)])
    
    # Partner Practitioners
    @api.depends("practitioner_ids")
    def _compute_practitioner_count(self):
        for rec in self:
            rec.practitioner_count = len(rec.practitioner_ids)

    practitioner_count = fields.Integer(compute=_compute_practitioner_count, string="Number of Practitioners", store=True)

    def action_view_practitioners(self):
        xmlid = "practitioner.action_practitioner_window"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        if self.practitioner_count > 1:
            action["domain"] = [("id", "in", self.practitioner_ids.ids)]
        else:
            action["views"] = [(self.env.ref("practitioner.view_practitioner_form").id, "form")]
            action["res_id"] = self.practitioner_ids and self.practitioner_ids.ids[0] or False
        return action
    
    # Partner Patients
    @api.depends("patient_ids")
    def _compute_patient_count(self):
        for rec in self:
            rec.patient_count = len(rec.patient_ids)

    patient_count = fields.Integer(
        compute=_compute_patient_count, string="Number of Patients", store=True
    )

    def action_view_patients(self):
        xmlid = "patient.action_patient_window"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        if self.patient_count > 1:
            action["domain"] = [("id", "in", self.patient_ids.ids)]
        else:
            action["views"] = [(self.env.ref("patient.view_patient_form").id, "form")]
            action["res_id"] = self.patient_ids and self.patient_ids.ids[0] or False
        return action

    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_customer_prescriptions(self):
        for records in self:
            return {
                'name':_('Prescriptions'),
                'view_type': 'form',
                'domain': [('customer', '=',records.id)],
                'res_model': 'practitioner.prescription',
                'view_id': False,
                'view_mode':'tree,form',
                'context':{'default_customer':self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['practitioner.prescription'].search_count([('customer','=',records.id)])
            records.prescription_count = count

  














