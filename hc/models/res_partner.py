from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    patient_ids = fields.One2many(
        comodel_name='hc.patient',
        inverse_name='partner_id',
        string="Patients",
    )

    patient_count = fields.Integer(
        string="Patient Count", store=False,
        compute='_compute_patient_count',
    )
    @api.depends('patient_ids')
    def _compute_patient_count(self):
        for partner in self:
            partner.patient_count = partner.patient_ids
        return

    is_patient = fields.Boolean(
        string="Patient", store=False,
        search='_search_is_patient',
    )
    def _search_is_patient(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('patient_ids', search_operator, False)]
