# import time
import calendar
import re

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _


class podiatry_practice(models.Model):
    ''' Defining Practice Information'''

    _name = 'podiatry.practice'
    _description = 'Podiatry Practice Information'
    _rec_name = "com_name"

    @api.constrains('code')
    def _check_code(self):
        for record in self:
            if self.env["podiatry.practice"].search(
                    [('code', '=', record.code), ('id', '!=', record.id)]):
                raise ValidationError("Podiatry Practice Code must be Unique")

    # @api.model
    # def _lang_get(self):
    #     '''Method to get language'''
    #     languages = self.env['res.lang'].search([])
    #     return [(language.code, language.name) for language in languages]

    company_id = fields.Many2one('res.company', 'Company', ondelete="cascade",
                                 required=True, delegate=True,
                                 help='Company_id of the practice')
    com_name = fields.Char('Practice Name', related='company_id.name',
                           store=True, help='Practice name')
    code = fields.Char('Code', required=True, help='Practice code')

    # lang = fields.Selection(_lang_get, 'Language',
    #                         help='''If the selected language is loaded in the
    #                             system, all documents related to this partner
    #                             will be printed in this language.
    #                             If not, it will be English.''')

    @api.model
    def create(self, vals):
        '''Inherited create method to assign company_id to practice'''
        res = super(podiatry_practice, self).create(vals)
        main_company = self.env.ref('base.main_company')
        res.company_id.parent_id = main_company.id
        return res
