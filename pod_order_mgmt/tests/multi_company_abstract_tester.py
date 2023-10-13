
from odoo import fields, models


class MultiCompanyAbstractTester(models.Model):
    _name = "multi.company.abstract.tester"
    _inherit = "multi.company.abstract"
    _description = "Multi Company Abstract Tester"

    name = fields.Char()
