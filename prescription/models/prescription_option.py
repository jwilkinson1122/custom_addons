# -*- coding: utf-8 -*-


from odoo import fields, models

from odoo.tools import formatLang


class PrescriptionOption(models.Model):
    _name = 'prescription.option'
    _description = 'Prescription Extras'

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    price = fields.Monetary('Price', required=True)
    partner_id = fields.Many2one('prescription.partner', ondelete='cascade')
    option_category = fields.Integer('Option Category', help="This field is a technical field", required=True, default=1)

    def name_get(self):
        currency_id = self.env.company.currency_id
        res = dict(super(PrescriptionOption, self).name_get())
        for option in self:
            price = formatLang(self.env, option.price, currency_obj=currency_id)
            res[option.id] = '%s %s' % (option.name, price)
        return list(res.items())
