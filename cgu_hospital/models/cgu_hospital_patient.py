from odoo import models, fields


class CGUHospitalPatient(models.Model):
    _name = 'cgu_hospital.patient'
    _inherit = ['cgu_hospital.contact.mixin', 'cgu_hospital.passport_data.mixin']
    _description = 'Patient'

    active = fields.Boolean(default=True)

    personal_doctor_id = fields.Many2one(
        comodel_name='cgu_hospital.doctor',
        string='Personal doctor')

    # personal_doctor_history_ids = fields.One2many(
    #     comodel_name='cgu_hospital.personal.doctor.history',
    #     inverse_name='patient_id',
    #     string='doctor history')
    #
    # visit_to_doctor_ids = fields.One2many(
    #     comodel_name='hr_hospital.visit.to.doctor',
    #     inverse_name='patient_id',
    #     string='visits history')

    # @api.onchange('personal_doctor_id')
    # def onchange_personal_doctor_id(self):
    #     for rec in self:
    #         lines = []
    #
    #         vals = {
    #             'date_medication': fields.Date.today(),
    #             'patient_id': rec.id,
    #             'doctor_id': rec.personal_doctor_id
    #         }
    #     lines.append((0, 0, vals))
    #     rec.personal_doctor_history_ids = lines
    #
    #
    # def open_list_personal_doctor_history(self):
    #     self.ensure_one()
    #     result = {
    #         "type": "ir.actions.act_window",
    #         "res_model": "hr_hospital.personal.doctor.history",
    #         # "domain": [('id', 'in', self.line_ids.move_id.move_id.ids), ('move_type', 'in', self.env['account.move'].get_sale_types())],
    #         # "context": {"create": False},
    #         "name": "personal doctor history",
    #         'view_mode': 'tree,form',
    #     }
    #     return result
    #
    # def open_list_visit_to_doctor(self):
    #     self.ensure_one()
    #     result = {
    #         "type": "ir.actions.act_window",
    #         "res_model": "hr_hospital.visit.to.doctor",
    #         # "domain": [('id', 'in', self.line_ids.move_id.move_id.ids), ('move_type', 'in', self.env['account.move'].get_sale_types())],
    #         # "context": {"create": False},
    #         "name": "visit to doctor",
    #         'view_mode': 'tree,form',
    #     }
    #     return result
    #
    # def open_list_diagnosis(self):
    #     self.ensure_one()
    #     result = {
    #         "type": "ir.actions.act_window",
    #         "res_model": "hr_hospital.diagnosis",
    #         # "domain": [('id', 'in', self.line_ids.move_id.move_id.ids), ('move_type', 'in', self.env['account.move'].get_sale_types())],
    #         # "context": {"create": False},
    #         "name": "diagnosis",
    #         'view_mode': 'tree,form',
    #     }
    #     return result
    #
