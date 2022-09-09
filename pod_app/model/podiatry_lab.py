# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime
# classes under  menu of laboratry


class podiatry_lab(models.Model):

    _name = 'podiatry.lab'
    _description = 'Podiatry Lab'

    name = fields.Char('ID')
    test_id = fields.Many2one('podiatry.test_type', 'Test Type', required=True)
    date_analysis = fields.Datetime(
        'Date of the Analysis', default=datetime.now())
    patient_id = fields.Many2one('podiatry.patient', 'Patient', required=True)
    date_requested = fields.Datetime('Date requested',  default=datetime.now())
    podiatry_lab_physician_id = fields.Many2one(
        'podiatry.physician', 'Pathologist')
    requestor_physician_id = fields.Many2one(
        'podiatry.physician', 'Physician', required=True)
    critearea_ids = fields.One2many(
        'podiatry_test.critearea', 'podiatry_lab_id', 'Critearea')
    results = fields.Text('Results')
    diagnosis = fields.Text('Diagnosis')
    is_invoiced = fields.Boolean(copy=False, default=False)

    @api.model
    def create(self, val):
        val['name'] = self.env['ir.sequence'].next_by_code('ltest_seq')
        result = super(podiatry_lab, self).create(val)
        if val.get('test_id'):
            critearea_obj = self.env['podiatry_test.critearea']
            criterea_ids = critearea_obj.search(
                [('test_id', '=', val['test_id'])])
            for id in criterea_ids:
                critearea_obj.write({'podiatry_lab_id': result})

        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
