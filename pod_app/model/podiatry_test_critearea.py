# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
# classes under cofigration menu of laboratry


class podiatry_test_critearea(models.Model):
    _name = 'podiatry_test.critearea'
    _description = 'podiatry test critearea'

    test_id = fields.Many2one('podiatry.test_type',)
    name = fields.Char('Name',)
    seq = fields.Integer('Sequence', default=1)
    podiatry_test_type_id = fields.Many2one('podiatry.test_type', 'Test Type')
    podiatry_lab_id = fields.Many2one('podiatry.lab', 'Podiatry Lab Result')
    warning = fields.Boolean('Warning')
    excluded = fields.Boolean('Excluded')
    lower_limit = fields.Float('Lower Limit')
    upper_limit = fields.Float('Upper Limit')
    lab_test_unit_id = fields.Many2one('podiatry.lab.test.units', 'Units')
    result = fields.Float('Result')
    result_text = fields.Char('Result Text')
    normal_range = fields.Char('Normal Range')
    remark = fields.Text('Remarks')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
