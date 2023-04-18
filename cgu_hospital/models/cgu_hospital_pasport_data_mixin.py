from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class CGUHospitalPassportDataMixin(models.AbstractModel):
    _name = 'cgu_hospital.passport_data.mixin'
    _description = 'Passport data mixin'

    date_birth = fields.Date()
    date_today = fields.Date(default=fields.Date.today)
    age = fields.Char(string='age', compute='_compute_age', store=True)

    passport_series = fields.Char(string="passport_series", size=2, )
    passport_number = fields.Char(string="passport_number", size=6, )
    passport_issued_when = fields.Date()
    passport_issued_whom = fields.Char()


@api.depends('date_birth')
def _compute_age(self):
    for record in self:
        if record.date_birth:
            record.age = relativedelta(fields.Date.today(), record.date_birth).years
        else:
            record.age = 0
