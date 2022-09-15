# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime
# classes under  menu of laboratry


class podiatry_patient_products_services(models.Model):
    _name = 'podiatry.patient.products.services'
    _description = 'podiatry patient products & services'
    _rec_name = 'patient_id'

    @api.model
    def default_get(self, fields):
        result = super(podiatry_patient_products_services,
                       self).default_get(fields)

        result.update({
            'user_id': self._uid,
        })
        return result

    patient_id = fields.Many2one('podiatry.patient', 'Patient', required=True)
    evaluation_start = fields.Datetime(
        'Date ', required=True, default=fields.Datetime.now)
    products_services_total = fields.Integer('PCS Total')
    user_id = fields.Many2one(
        'res.users', 'Healh Professional', default=lambda self: self.env.user)
    notes = fields.Text('Notes')
    # selection field
    products_services_aches_pains = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Complains of aches and pains')
    products_services_absent_from_school = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Absent from school')
    products_services_act_as_younger = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Acts younger than children his or her age')
    products_services_acts_as_driven_by_motor = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Acts as if driven by a motor')
    products_services_afraid_of_new_situations = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Is afraid of new situations')
    products_services_blames_others = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Blames others for his or her troubles')
    products_services_daydreams_too_much = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Daydreams too much')
    products_services_distracted_easily = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Distracted easily')
    products_services_does_not_get_people_feelings = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Does not get people feelings')
    products_services_does_not_listen_to_rules = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Does not listen to rules')
    products_services_does_not_show_feelings = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Does not show feelings')
    products_services_down_on_self = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Is down on him or herself')
    products_services_feels_hopeless = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Feels hopeless')
    products_services_feels_is_bad_child = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Feels he or she is bad')
    products_services_fidgety = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Fidgety, unable to sit still')
    products_services_fights_with_others = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Fights with other children')
    products_services_gets_hurt_2 = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Gets hurt frequently')
    products_services_having_less_fun = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Seems to be having less fun')
    products_services_irritable_angry = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Is irritable, angry')
    products_services_less_interested_in_friends = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Less interested in friends')
    products_services_less_interest_in_school = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Less interested in school')
    products_services_refuses_to_share = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Refuses to share')
    products_services_sad_unhappy = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Feels sad, unhappy')
    products_services_school_grades_dropping = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'School grades dropping')
    products_services_spend_time_alone = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Spends more time alone')
    products_services_takes_things_from_others = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Takes things that do not belong to him or her')
    products_services_takes_unnecesary_risks = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Takes unnecessary risks')
    products_services_teases_others = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Teases others')
    products_services_tires_easily = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Tires easily, has little energy')
    products_services_trouble_concentrating = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Has trouble concentrating')
    products_services_trouble_sleeping = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Has trouble sleeping')
    products_services_trouble_with_teacher = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Has trouble with teacher')
    products_services_gets_hurt_often = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Gets hurt often')
    products_services_visit_doctor_finds_ok = fields.Selection([('0', 'Never'), ('1', 'Sometimes'), (
        '2', 'Often')], 'Visits the doctor with doctor finding nothing wrong')
    products_services_wants_to_be_with_parents = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Wants to be with you more than before')
    products_services_worries_a_lot = fields.Selection(
        [('0', 'Never'), ('1', 'Sometimes'), ('2', 'Often')], 'Worries a lot')

    @api.onchange('products_services_aches_pains',
                  'products_services_absent_from_school',
                  'products_services_act_as_younger', 'products_services_acts_as_driven_by_motor',
                  'products_services_afraid_of_new_situations',
                  'products_services_blames_others', 'products_services_teases_others',
                  'products_services_daydreams_too_much', 'products_services_tires_easily',
                  'products_services_distracted_easily', 'products_services_trouble_concentrating',
                  'products_services_trouble_sleeping', 'products_services_trouble_with_teacher',
                  'products_services_visit_doctor_finds_ok', 'products_services_wants_to_be_with_parents',
                  'products_services_worries_a_lot',
                  'products_services_does_not_get_people_feelings', 'products_services_does_not_listen_to_rules',
                  'products_services_does_not_show_feelings', 'products_services_down_on_self',
                  'products_services_feels_hopeless', 'products_services_feels_is_bad_child',
                  'products_services_fidgety', 'products_services_fights_with_others',
                  'products_services_gets_hurt_often', 'products_services_having_less_fun', 'products_services_irritable_angry',
                  'products_services_less_interested_in_friends', 'products_services_less_interest_in_school',
                  'products_services_refuses_to_share', 'products_services_sad_unhappy',
                  'products_services_school_grades_dropping', 'products_services_spend_time_alone',
                  'products_services_takes_things_from_others', 'products_services_takes_unnecesary_risks', )
    def onchange_selections(self):
        self.products_services_total = int(self.products_services_aches_pains)+int(self.products_services_absent_from_school) + int(self.products_services_act_as_younger) + int(self.products_services_acts_as_driven_by_motor) + int(self.products_services_afraid_of_new_situations) + int(self.products_services_blames_others) + int(self.products_services_teases_others) + int(self.products_services_daydreams_too_much)+int(self.products_services_tires_easily) + int(self.products_services_distracted_easily) + int(self.products_services_trouble_concentrating) + int(self.products_services_trouble_sleeping) + int(self.products_services_trouble_with_teacher) + int(self.products_services_visit_doctor_finds_ok)++int(self.products_services_wants_to_be_with_parents) + int(self.products_services_worries_a_lot) + int(
            self.products_services_does_not_get_people_feelings)+int(self.products_services_down_on_self) + int(self.products_services_feels_hopeless) + int(self.products_services_feels_is_bad_child)+int(self.products_services_fidgety) + int(self.products_services_fights_with_others) + int(self.products_services_gets_hurt_often) + int(self.products_services_having_less_fun) + int(self.products_services_irritable_angry) + int(self.products_services_less_interested_in_friends)+int(self.products_services_less_interest_in_school) + int(self.products_services_refuses_to_share) + int(self.products_services_sad_unhappy) + int(self.products_services_school_grades_dropping) + int(self.products_services_spend_time_alone) + int(self.products_services_takes_things_from_others)+int(self.products_services_takes_unnecesary_risks)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
