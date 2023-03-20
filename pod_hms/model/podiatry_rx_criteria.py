# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
# classes under cofigration menu of laboratry


class podiatry_rx_criteria(models.Model):
    _name = 'podiatry_rx.criteria'
    _description = 'podiatry test criteria'

    rx_id = fields.Many2one('podiatry.rx_type',)
    name = fields.Char('Name',)
    seq = fields.Integer('Sequence', default=1)
    podiatry_rx_type_id = fields.Many2one('podiatry.rx_type', 'Test Type')
    podiatry_rx_id = fields.Many2one('podiatry.rx', 'Medical Rx Result')
    warning = fields.Boolean('Warning')
    excluded = fields.Boolean('Excluded')
    lower_limit = fields.Float('Lower Limit')
    upper_limit = fields.Float('Upper Limit')
    rx_unit_id = fields.Many2one('podiatry.rx.units', 'Units')
    result = fields.Float('Result')
    result_text = fields.Char('Result Text')
    normal_range = fields.Char('Normal Range')
    remark = fields.Text('Remarks')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
