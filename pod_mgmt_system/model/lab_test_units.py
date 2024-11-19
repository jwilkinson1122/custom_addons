# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

# classes under cofigration menu of laboratry


class lab_test_units(models.Model):

    _name = "lab.test.units"
    _description = "Lab Test Units"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
