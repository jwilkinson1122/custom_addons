# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class pod_doctor(models.Model):
    _name = "pod.doctor"
    _description = 'podiatry doctor'
    _rec_name = 'partner_id'

    doctor_name = fields.Char(string='Name', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', 'Doctor', required=True)
    practice_partner_id = fields.Many2one(
        'res.partner', domain=[('is_practice', '=', True)], string='Medical Practice')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')
    active = fields.Boolean(string="Active", default=True)

    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('doctor_name'):
            default['doctor_name'] = _("%s (Copy)", self.doctor_name)
        default['note'] = "Copied Record"
        return super(pod_doctor, self).copy(default)

    # def _compute_prescription_count(self):
    #     for rec in self:
    #         prescription_count = self.env['pod.rx.order'].search_count(
    #             [('partner_id', '=', rec.id)])
    #         rec.prescription_count = prescription_count

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['pod.prescription.request'].search_count(
                [('doctor_id', '=', rec.id)])
            rec.prescription_count = prescription_count
