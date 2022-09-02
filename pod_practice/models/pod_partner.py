

from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class PodPartner(models.Model):
    _name = 'pod.partner'
    _description = 'Podiatry Partner Abstract from res.partner'
    _inherit = 'res.patient'
#    _inherits = {'res.partner': 'partner_id'}
    _inherit = 'mail.thread'

#    def _get_pod_entity(self):
#        self.ensure_one()
#        if self.type and self.type[:15] == 'pod':
#            return self.env[self.type].search([
#                ('partner_id', '=', self.id),
#            ])

    def _count_patients(self):

        # TODO:Test this with assigned patients
        for record in self:
            try:
                patients = False
                # patients = self.env['pod.patient'].search([
                #     ('partner_id', 'child_of', record.id),
                # ])[0]
                if patients:
                    print(76)
                    record.count_patients = len(patients)
                else:
                    record.count_patients = 0
            except Exception as e:
                print(78, e)
                record.count_patients = 0

    def compute_age_from_dates(
        self, dob, gender, caller, extra_date
    ):
        """ Get the person's age.
            Calculate the current age of the patient.
            Returns:
            If caller == 'age': str in Y-M-D,
                caller == 'raw_age': [Y, M, D]"""
        today = datetime.today().date()
        if dob:
            start = datetime.strptime(str(dob.date()), '%Y-%m-%d')
            end = datetime.strptime(str(today), '%Y-%m-%d')
            if extra_date:
                end = datetime.strptime(str(extra_date.date()), '%Y-%m-%d')
            rdelta = relativedelta(end, start)
            years_months_days = str(rdelta.years) + 'a ' \
                + str(rdelta.months) + 'm ' \
                + str(rdelta.days) + 'd'
        else:
            return None
        if caller == 'age':
            return years_months_days
        elif caller == 'raw_age':
            return [rdelta.years, rdelta.months, rdelta.days]
        else:
            return None

    @api.constrains('birthdate_date')
    def _check_birthdate_date(self):
        """ It will not allow birthdates in the future. """
        now = datetime.now()
        for record in self:
            print(record)
            if not record.birthdate_date:
                continue
            birthdate = fields.Datetime.from_string(record.birthdate_date)
            if birthdate > now:
                raise ValidationError('Partners cannot be born in the future.')
            print(
                record.birthdate_date, record.deceased, record.date_death,
                record.gender, 'age'
            )
            record.age = self.compute_age_from_dates(
                record.birthdate_date, record.deceased, record.date_death,
                record.gender, 'age', False
            )

    @api.model
    def create(self, vals):
        """ It overrides create to bind appropriate entity. """
        if all((
            vals.get('type', '').startswith('pod.'),
            not self.env.context.get('pod_entity_no_create'),
        )):
            model = self.env[vals['type']].with_context(
                pod_entity_no_create=True,
            )
            pod_entity = model.create(vals)
#            return pod_entity.partner_id
            return pod_entity.partner_id
        # tmp_act = self.generate_puid()
        # for values in vals:
        #     if not values.get('ref'):
        #         values['ref'] = values.get('self.country_id')[3:]
        #     else:
        #         values['ref'] = tmp_act
        #     if 'unidentified' in values and values['unidentified']:
        #         values['ref'] = 'NN-' + values.get('ref')
        return super(PodPartner, self).create(vals)
