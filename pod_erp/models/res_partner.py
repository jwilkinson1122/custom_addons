from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class InheritedResPartner(models.Model):
    _inherit = 'res.partner'

    # is_patient = fields.Boolean('Patient')
    # is_practitioner = fields.Boolean('Practitioner')

    # patient_identifier = fields.Char(readonly=True)
    # practitioner_identifier = fields.Char(readonly=True)

    # @api.model
    # def _get_podiatry_identifiers(self):
    #     res = super(InheritedResPartner, self)._get_podiatry_identifiers()
    #     res.append(
    #         (
    #             "is_patient",
    #             "is_practitioner",
    #             "practitioner_identifier",
    #             "patient_identifier",
    #             self._get_practitioner_identifier,
    #             self._get_patient_identifier,
    #         )
    #     )
    #     return res

    # @api.model
    # def _get_practitioner_identifier(self, vals):
    #     return self.env["ir.sequence"].next_by_code("podiatry.practitioner") or "ID"

    # def _get_patient_identifier(self, vals):
    #     return self.env["ir.sequence"].next_by_code("podiatry.patient") or "PID"

    # @api.model
    # def default_podiatry_fields(self):
    #     result = super(InheritedResPartner, self).default_podiatry_fields()
    #     result.append("is_practitioner")
    #     return result

    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_customer_prescriptions(self):
        for records in self:
            return {
                'name': _('Prescription'),
                'view_type': 'form',
                'domain': [('customer', '=', records.id)],
                'res_model': 'podiatry.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_customer': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['podiatry.prescription'].search_count(
                [('customer', '=', records.id)])
            records.prescription_count = count
