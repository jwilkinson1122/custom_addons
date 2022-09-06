from dateutil.relativedelta import relativedelta

from odoo import fields,api,models
from odoo.exceptions import UserError
import re
from odoo.exceptions import ValidationError
from datetime import date, datetime


class Patients(models.Model):
    _name="hospital.patient"
    _sql_constraints = [
        ('unique_email', 'unique (email)', 'Email address already exists!')
    ]
    firstname=fields.Char(required=True)
    lastname=fields.Char(required=True)
    email=fields.Text()
    birth_date=fields.Date()
    age = fields.Integer(compute="calc_age",store=True)
    history= fields.Html()
    description=fields.Char()
    cr_ratio= fields.Float()
    blood_type = fields.Selection(
        [
         ('A', 'A'),
         ('B', 'B'),
         ('AB', 'AB'),
         ],default='A'
    )

    state=fields.Selection([
        ('Undetermined', 'Undetermined'),
        ('Good', 'Good'),
        ('fair', 'fair'),
    ])
    pcr= fields.Boolean()
    image=fields.Binary()
    address=fields.Text()


    date1=fields.Date()

    # relations

    departments_ids=fields.Many2one('hms.departments')
    department_name=fields.Char(related='departments_ids.name')
    department_capacity=fields.Integer(related='departments_ids.capacity')

    tags_ids = fields.Many2many("hms.tags")


    @api.onchange('age')
    def _onchange_age(self):
        print(self.id)
        mesg=""
        if self.age > 30:
            self.pcr = False
            mesg = "age more 30"
        else:
            self.pcr = True
            mesg = "age less 30"
        return {
            'warning': {
                'title': 'Hello',
                'message': mesg
            },
        }

    @api.onchange('email')
    def validate_mail(self):
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            if match == None:
                raise ValidationError('Not a valid E-mail ID')

    @api.depends('birth_date')
    def calc_age(self):
        for patient in self:
            if patient.birth_date:
                d1 = datetime.strptime(str(self.birth_date),"%Y-%m-%d").date()
                d2 = date.today()
                self.age = relativedelta(d2, d1).years


