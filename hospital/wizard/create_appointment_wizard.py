from odoo.models import TransientModel
from odoo import fields, api


class CreateAppointmentWizard(TransientModel):
    _name = 'create.appointment.wizard'
    _description = 'Create Appointment Wizard'
    _inherit = ['hospital.appointment']

    name = fields.Char(
        string='Name',
        required=False)

    @api.model
    def default_get(self, fields):
        print("enter create.appointment.wizard's default")
        result = super(CreateAppointmentWizard, self).default_get(fields)
        if self._context.get('active_id'):
            result['patient_id'] = self._context.get('active_id')
        return result

    # current_patient_name = fields.Char(related='patient_id.patient_name')

    #
    # patient_id = fields.Many2one(
    #     comodel_name='hospital.patient',
    #     string='Patient_id',
    #     required=False)


    def create_appointment_action(self):
        print('#' * 80)
        data = {
            'name': self.name,
            'patient_id': self.patient_id.id,
            'appointment_date': self.appointment_date,
            'checkup_date': self.checkup_date,

        }
        # # method1
        new_appointment = self.env['hospital.appointment'].create(data)
        self.patient_id.message_post(body="appointment created successfully")
        # action = self.env.ref('hospital.appointment_act_window').read()[0]
        # action['view_mode'] = 'tree'
        # action['domain'] = [('patient_id', '=', self.patient_id.id)]
        # action['target'] = 'new'
        # action['res_id'] = new_appointment.id
        #
        # return action
        # # method2
        # return {
        #     'name': 'new app',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': "tree",
        #     'res_model': 'hospital.appointment',
        #     'res_id': new_appointment.id,
        #     'target': "current"
        #
        # }

    def view_appointment_action(self):
        # # method1
        return {
            'name': f'{self.patient_id.patient_name} appointments',
            'type': 'ir.actions.act_window',
            'view_mode': "tree",
            'res_model': 'hospital.appointment',
            'res_id': self.patient_id.id,
            'target': "new",
            'domain': [('patient_id', '=', self.patient_id.id)]
        }

    def test(self):
        print("hooooooooooooooooooooooooooooooo")
        return "105"
        # method2
        # action = self.env.ref('hospital.appointment_act_window').read()[0]
        # action['view_mode'] = 'tree'
        # action['domain'] = [('patient_id', '=', self.patient_id.id)]
        # action['target'] = 'current'
        # return action

        # # method3
        # action = self.env['ir.actions.actions']._for_xml_id(
        #     'hospital.appointment_act_window')
        # action['domain'] = [('patient_id', '=', self.patient_id.id)]
        # action['target'] = 'new'
        # return action
