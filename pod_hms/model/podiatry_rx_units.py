# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
# classes under cofigration menu of laboratry


class podiatry_rx_units(models.Model):

    _name = 'podiatry.rx.units'
    _description = 'Medical Rx Units'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
