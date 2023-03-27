
from odoo import api, fields, models


class Patient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # 5.Model Inheritance
    _description = "Hospital Patient"
    _order = "id desc"

    # 1.
    # fields dökümandan anlatıldıktan sonra burada açılacak
    name = fields.Char(string='Name', required=True)
    image = fields.Binary(string="Patient Image")
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='male', tracking=True)

    doctor_ids = fields.Many2many('hospital.doctor', 'doctor_patient_rel', string="Doctors")

    # 2.
    # basic alanlar bittikten sonra appointment'a ilgili alanları ekle ve one2many ilişki oluştur
    responsible_id = fields.Many2one('res.partner', string="Responsible")

    appointment_ids = fields.One2many(
        'hospital.appointment', 'patient_id', string="Appointments")
    # 3 Basic view

    # 4 Decorators
    appointment_count = fields.Integer(
        string="Appointment Count", compute="_compute_appointment", )
    note = fields.Text(string='Description', compute="_compute_description")
    responsible_name = fields.Char("Resp. Name", related="responsible_id.name")

    color = fields.Integer()  # Color for Custom Widget
    mail = fields.Char("Mail",)

    def get_default_user(self):
        return self.env.user

    user_id = fields.Many2one(
        'res.users', string="User", default=get_default_user)

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'Name must be unique'),
    ]

    @api.depends('appointment_ids')
    def _compute_appointment(self):
        for record in self:
            record.appointment_count = len(record.appointment_ids.ids)
            # Save edildikten sonra appointment_count doğru hesaplanıyor

    def _inverse_appointment(self):
        print("alan değiştiriliyor...............................")

    @api.depends("responsible_id.name")
    def _compute_description(self):
        for record in self:
            record.note = "Test for patient %s" % record.responsible_id.name

    # CRUD#####5 Python Inheritance

    @api.model
    def create(self, vals):
        patient_name = vals.get('name')
        illness = vals.get('note')
        msg = f'The {patient_name} has {illness}, please help!'
        res = super().create(vals)
        res.message_post(body=msg,message_type='notification', author_id=self.env.user.id,partner_ids=[2,6],)
        return res

    def write(self, vals):
        self.message_post(body=vals)
        return super().write(vals)

    def unlink(self):
        if self.appointment_ids:
            print("cant delete")
        return super().unlink()

    # 7 Business Flow

    def action_view_appointment(self):

        view = {
            'name': f'Appointments of {self.name}',
            'view_mode': 'tree',
            'res_model': 'hospital.appointment',
            'view_id': self.env.ref('hospital_management.hospital_appointment_tree_view').id,
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.id)],
            'context': {}
        }

        return view


# 5 model inheritance extend
class DoctorInherit(models.Model):
    _inherit = 'hospital.doctor'

    is_available = fields.Boolean(default=True)

    def get_doctor_info(self):
        for rec in self:
            info = f'doctor id: {rec.id}, doctor name:{rec.name}, availability: {rec.is_available}'
            print(info)

    #11. External Api
    def get_doctor(self, doctor_list):
        doctors = self.browse(doctor_list)
        infos = []
        for doctor in doctors:
            info = f'doctor id: {doctor.id}, doctor name:{doctor.name}, availability: {doctor.is_available}'
            infos.append(info)
        
        return infos