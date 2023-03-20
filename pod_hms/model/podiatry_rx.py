# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime
# classes under  menu of laboratry


class podiatry_rx(models.Model):

    _name = 'podiatry.rx'
    _description = 'Medical Rx'

    name = fields.Char('ID')
    rx_id = fields.Many2one('podiatry.rx_type', 'Test Type', required=True)
    date_analysis = fields.Datetime(
        'Date of the Analysis', default=datetime.now())
    patient_id = fields.Many2one('podiatry.patient', 'Patient', required=True)
    date_requested = fields.Datetime('Date requested',  default=datetime.now())
    podiatry_rx_practitioner_id = fields.Many2one(
        'podiatry.practitioner', 'Pathologist')
    requestor_practitioner_id = fields.Many2one(
        'podiatry.practitioner', 'Practitioner', required=True)
    criteria_ids = fields.One2many(
        'podiatry_rx.criteria', 'podiatry_rx_id', 'Critearea')
    results = fields.Text('Results')
    diagnosis = fields.Text('Diagnosis')
    is_invoiced = fields.Boolean(copy=False, default=False)

    @api.model
    def create(self, val):
        val['name'] = self.env['ir.sequence'].next_by_code('pod_rx_seq')
        result = super(podiatry_rx, self).create(val)
        if val.get('rx_id'):
            criteria_obj = self.env['podiatry_rx.criteria']
            criterea_ids = criteria_obj.search(
                [('rx_id', '=', val['rx_id'])])
            for id in criterea_ids:
                criteria_obj.write({'podiatry_rx_id': result})

        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
