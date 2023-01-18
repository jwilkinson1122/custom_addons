
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ClinicCheckup(models.Model):
    _name = "clinic.checkup"
    _description = "Checkup"
    _order = "name desc"

    # @api.depends('patient_id')
    # def _get_age(self):
    #     age = False
    #     if self.patient_id:
    #         age = datetime.now().year - datetime.strptime(self.patient_id.birth_date, '%Y-%m-%d').year
    #     self.age = age

    birthdate = fields.Datetime(string="Birthdate")
    age = fields.Char(compute='_get_age')

    @api.model
    def _relativedelta_to_text(self, delta):
        result = []

        if delta:
            if delta.years > 0:
                result.append(
                    "{years} {patient}".format(
                        years=delta.years,
                        patient=_("year") if delta.years == 1 else _("years"),
                    )
                )
            if delta.months > 0 and delta.years < 9:
                result.append(
                    "{months} {patient}".format(
                        months=delta.months,
                        patient=_("month") if delta.months == 1 else _(
                            "months"),
                    )
                )
            if delta.days > 0 and not delta.years:
                result.append(
                    "{days} {patient}".format(
                        days=delta.days,
                        patient=_("day") if delta.days == 1 else _("days"),
                    )
                )

        return bool(result) and " ".join(result)

    @api.depends('birthdate')
    def _get_age(self):
        now = fields.Datetime.now()
        for patient in self:
            delta = relativedelta(now, patient.birthdate)
            patient.age = self._relativedelta_to_text(delta)

        return

    name = fields.Char(string='Checkup', default='/')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled')
    ], string='State', default='draft')
    register_id = fields.Many2one(
        'clinic.register', 'Register', track_visibility='onchange')
    date = fields.Datetime(
        string='Date', default=lambda self: fields.datetime.now())
    patient_id = fields.Many2one(related='register_id.patient_id',
                                 string='Patient', change_default=True, track_visibility='onchange')
    gender = fields.Selection(
        related='register_id.patient_id.gender', string='Gender')
    age = fields.Integer(compute='_get_age', string='Age')
    poly_id = fields.Many2one(related='register_id.poly_id', string='Poly')
    doctor_id = fields.Many2one(
        'res.partner.doctor', string='Doctor', track_visibility='onchange')
    complain = fields.Text(string='Complain')
    checkup_result = fields.Text(string='Checkup Result')
    medication = fields.Text(string='Medication')
    prescription = fields.One2many(
        'clinic.prescription', 'checkup_id', 'Medical Prescription')
    note = fields.Text(related='register_id.note', string="Note")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'clinic.checkup.sequence')
        return super(ClinicCheckup, self).create(vals)

    def action_confirm(self):
        clinic_invoice = self.env['clinic.invoice']
        for me_id in self:
            if me_id.state == 'draft':
                inv_line_vals = []
                for line in me_id.prescription:
                    inv_line_vals.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.name_get()[0][1],
                        'quantity': line.qty,
                        'price_unit': line.product_id.lst_price,
                        # 'account_id' : me_id.patient_id.property_account_payable_id.id,
                    }))
                if line.qty < 0:
                    raise Warning('please input qty')
                clinic_invoice.create({
                    'partner_id': me_id.patient_id.id,
                    'invoice_line_ids': inv_line_vals,
                })
                me_id.write({'state': 'confirm'})

    def action_cancel(self):
        view_id = self.env.ref('new_clinic.view_clinic_reason_cancel_wizard')
        return {
            'name': 'Reason Cancel',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'clinic.reason.cancel.wizard',
            'views': [(view_id.id, 'form')],
            'view_id': view_id.id,
            'target': 'new',
        }

    def unlink(self):
        for me_id in self:
            if me_id.state != 'draft':
                raise Warning('Cannot delete data')
        return super(ClinicCheckup, self).unlink()


class ClinicPrescription(models.Model):
    _name = "clinic.prescription"
    _description = "Prescription"
    _rec_name = "product_id"

    checkup_id = fields.Many2one('clinic.checkup', 'Checkup')
    product_id = fields.Many2one('product.product', 'Medicine', required="1")
    medication_use = fields.Char('Medication Usage')
    medication_time = fields.Selection([
        ('before', 'Before'),
        ('after', 'After'),
    ], 'Before/After meal', default='after')
    qty = fields.Float('Quantity')

    @api.onchange
    def change_product(self):
        if self.product_id:
            self.unit_id = self.product_id.uom_id.id
