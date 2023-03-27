from tabnanny import check
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class Appointment(models.Model):
    _name = "hospital.appointment"
    _inherits = {'sale.order': 'bill_appointment_id'} #5 Model Inheritance Delegation
    _description = "Hospital Appointment"
    _inherit = ['mail.thread'] #9-Reports

    reference = fields.Char(string='Reference', required=True,
                       copy=False, readonly=True,  default=lambda self: _('New'))
    patient_id = fields.Many2one(
        'hospital.patient', string="Patient", required=True)
    doctor_id = fields.Many2one(
        'hospital.doctor', string="Doctor", required=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('done', 'Done'), ('cancel', 'Cancelled')], default='draft',
                             string="Status",)
    date_appointment = fields.Date(string="Date")
    date_checkup = fields.Datetime(string="Check Up Time")
    prescription = fields.Text(string="Prescription")
    bill_appointment_id = fields.Many2one('sale.order', 'Bill of Appointment', required=True, ondelete="cascade")#5 Model Inheritance Delegation

    # 4 Decorators
    @api.onchange('date_checkup')
    def onchange_check_up(self):
        check_up = self.date_checkup
        if check_up and check_up.hour>18:
            self.date_appointment = self.date_appointment + relativedelta(days=1)
            return {
                'warning': {
                    'title': 'Warning',
                    'message': 'Appointment date changed.',
                    'type':'notification'
                }
            }


    @api.constrains('name','prescription')
    def _constrains_name(self):
        if self.name == self.prescription:
            raise ValidationError("Name and Prescription must be different")


    @api.constrains('date_appointment','date_checkup')
    def _constraint_date(self):
        today = fields.Date.today()
        now = fields.Datetime.now()

        if self.date_appointment<today or self.date_checkup<now:
            raise ValidationError("App date and time not true")
    

    ###########7 Business Flowww

    def action_confirm(self):
        # template = self.env.ref('hospital_management.hospital_appointment_confirm_mail_template')#9-Reports
        # attachment = self.env['ir.attachment'].search([('id','=',1)])#9-Reports
        # template.attachment_ids = [(4,attachment.id)]#9-Reports
        # self.message_post_with_template(template.id)#9-Reports
        print("amount total:", self.amount_total)

        
        #self.state = 'confirm'
    
    
    
    def action_done(self):
        self.state = 'done'
    
    
    
    def action_cancel(self):
        self.state = 'cancel'


    
    def create_appointment_list(self, frequent):
        if frequent == 'daily':
            today = fields.Date.today()
            appointments = self.env['hospital.appointment'].search([('date_appointment', '>', today)])
            app_list = []
            for app in appointments:
                vals = {
                    'patient':app.patient_id.name,
                    'doctor':app.doctor_id.name,
                    'date':app.date_appointment,
                    'prescription':app.prescription
                }
                app_list.append(vals)
            
            with open("app_list.txt", "w") as f:
                for app in app_list:
                    f.write(str(app)+"\n")




    @api.model
    def create(self, vals):
        create_mode = self.env.context.get('create_mode')
        if create_mode == 'wizard':
            vals.update({
                'name':"created by wizard"
            })
        return super().create(vals)

    
    #9-Reports
    def report_pdf(self):
        report_obj = self.env.ref('hospital_management.action_hospital_appointment_report')
        data = {'mode':"created by button"}
        return report_obj.report_action(self, data=data)