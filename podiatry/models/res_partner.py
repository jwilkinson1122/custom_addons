from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    #  Patient
    patient_id = fields.One2many(
        comodel_name='podiatry.patient',
        inverse_name='partner_id',
        string="Patients",
    )

    patient_count = fields.Integer(
        string="Patient Count", store=False,
        compute='_compute_patient_count',
    )

    @api.depends('patient_id')
    def _compute_patient_count(self):
        for partner in self:
            partner.patient_count = partner.patient_id
        return

    is_patient = fields.Boolean(
        string="Patient", store=False,
        search='_search_is_patient',
    )

    def _search_is_patient(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('patient_id', search_operator, False)]

    # Practitioner
    practitioner_id = fields.One2many(
        comodel_name='podiatry.practitioner',
        inverse_name='partner_id',
        string="Practitioners",
    )

    practitioner_count = fields.Integer(
        string="Practitioner Count", store=False,
        compute='_compute_practitioner_count',
    )

    @api.depends('practitioner_id')
    def _compute_practitioner_count(self):
        for partner in self:
            partner.practitioner_count = partner.practitioner_id
        return

    is_practitioner = fields.Boolean(
        string="Practitioner", store=False,
        search='_search_is_practitioner',
    )

    def _search_is_practitioner(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('practitioner_id', search_operator, False)]
