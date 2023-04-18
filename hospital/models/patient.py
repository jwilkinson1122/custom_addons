from odoo import api, fields, models
from datetime import datetime


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_name'
    _order = 'patient_name desc'
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        required=False)
    patient_seq = fields.Char(string='Patient_seq', required=True, copy=False,
                              readonly=True, default='new')
    patient_name = fields.Char(string='Patient Name', required=True)
    patient_age = fields.Integer(string='Patient Age', required=True,
                                 tracking=True
                                 )
    email = fields.Char(string='Email', required=False,
                        default='hassanmahmoud607@gmail.com')
    gender = fields.Selection(string='Gender',
                              selection=[
                                  ('male', 'Male'),
                                  ('female', 'Female'),
                                  ('other', 'Other')], required=True,
                              default='other')

    notes = fields.Text(string="Notes", required=False, tracking=True)
    state = fields.Selection(
        [
            ('urgent', 'Urgent'),
            ('normal', 'Normal'),
            ('naction', 'Need Action')], string='Status', required=True,
        tracking=True
        # default='normal'
    )

    related_parent = fields.Many2one(comodel_name='hospital.parent',
                                     string='parent name', required=False)
    appointment_counter = fields.Integer(string='Appointment_counter',
                                         required=False,
                                         compute='_compute_appointment_counter'
                                         )

    rel_appointments = fields.One2many(comodel_name='hospital.appointment',
                                       inverse_name='patient_id')
    image = fields.Binary(string="patient image")

    def _compute_appointment_counter(self):
        for record in self:
            appointment_counter = record.env[
                'hospital.appointment'].search_count(
                [('patient_id', '=', record.id)])
            print(appointment_counter)
            record.appointment_counter = appointment_counter

    def to_urgent(self):
        self.state = 'urgent'

    def to_normal(self):
        self.state = 'normal'

    def to_action(self):
        print(f" {self._context.get('active_id')} ".center(80, "&"))
        self.state = 'naction'

    def to_google(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://www.google.com',
            'target': 'new'
        }

    def send_patient_email(self):
        print("sending ....")
        tem_id = self.env.ref('hospital.patient_mail_template').id
        print(tem_id)
        tem = self.env['mail.template'].browse(tem_id)
        print(tem)
        tem.send_mail(self.id, force_send=True)
        print("sent")

    @api.model
    def create(self, vals_list):
        vals_list['patient_seq'] = self.env['ir.sequence'].next_by_code(
            'code.patient.seq')
        obj = super(HospitalPatient, self).create(vals_list)
        return obj

    @api.model
    def default_get(self, fields):
        result = super(HospitalPatient, self).default_get(fields)
        print(result)
        return result

    def to_appointments(self):
        action = self.env.ref('hospital.appointment_act_window').read()[0]
        action['view_mode'] = 'tree, form'
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.id}
        action['target'] = 'new'
        return action

        # return {
        #     'name': f'{self.patient_name} appointments',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': "tree",
        #     'res_model': 'hospital.appointment',
        #     # 'res_id': self.id,
        #     'target': "new",
        #     'domain': [('patient_id', '=', self.id)]
        # }
