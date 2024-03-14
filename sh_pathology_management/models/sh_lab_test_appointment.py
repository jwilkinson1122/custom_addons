# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api
import datetime
import uuid


class Appointment(models.Model):
    _name = 'sh.patho.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Appointment Detail"

    name = fields.Char(readonly=True)
    state_type = fields.Selection([('new', 'New'), ('done', 'Done'), (
        'cancel', 'Cancel')], default="new", string="Status", tracking=True)
    patient_id = fields.Many2one(
        'res.partner', string="Patient", tracking=True,)
    technician_id = fields.Many2one('res.partner', string="Technician")
    lab_center_id = fields.Many2one('sh.lab.center', string="Laboratory")
    collection_center_id = fields.Many2one(
        'sh.collection.center', string="Collection",
        domain="[('laboratory_id', '=?', lab_center_id)]"
    )
    request_line = fields.One2many(
        'sh.patho.request.line', 'patho_request_id', copy=True, auto_join=True)
    note = fields.Text()
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company)
    user_id = fields.Many2one(
        'res.users', required=False, default=lambda self: self.env.user)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id,
                                  string='Currency', store=True, depends=["company_id"],)

    amount_untaxed = fields.Monetary(
        compute="_amount_untaxed_compute", currency_field="currency_id", store=True, readonly=True)
    amount_tax = fields.Monetary(
        compute="_amount_tax_compute", currency_field="currency_id", store=True, readonly=True)
    amount_total = fields.Monetary(
        compute="_amount_total_compute", currency_field="currency_id",  store=True, readonly=True)
    total_diagnosis = fields.Integer(compute="get_total_of_diagnosis")
    appointment_date = fields.Datetime(
        string="Appointment", tracking=True, default=lambda self: fields.datetime.now(),)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name.replace("/", "_"))

    # Send By Email Button Action
    def action_send_email(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env.ref(
            'sh_pathology_management.email_template_sh_patho_lab_request', raise_if_not_found=False).id

        ctx = {
            'default_model': 'sh.patho.request',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_appointment_as_sent': True,
            'custom_layout': 'mail.mail_notification_light',
            'force_email': True,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_appointment_as_sent'):
            if kwargs and kwargs.get('partner_ids'):
                self.message_subscribe(partner_ids=kwargs.get('partner_ids'))

        return super(Appointment, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    report_token = fields.Char("Access Token")

    def _get_token(self):
        """ Get the current record access token """
        if self.report_token:
            return self.report_token
        else:
            report_token = str(uuid.uuid4())
            self.write({'report_token': report_token})
            return report_token

    def get_download_report_url(self):
        url = ''
        if self.id:
            self.ensure_one()
            url = '/download/diagnosis/' + '%s?access_token=%s' % (
                self.id,
                self._get_token()
            )
        return url

    def action_send_whatsapp_msg(self):

        phone = self.patient_id.mobile

        name = "Dear%20" + self.patient_id.name + ",%0A%0A"

        text = 'Your Appointment%20' + '*' + self.name + '*' + '%20 amounting in%20' + \
               '*' + str(self.currency_id.symbol) + str(self.amount_total) + '*' + \
               '%20 is ready.%0A%0AFollowing is your test details.%0A%0A'

        product_and_price = ''
        for data in self.request_line:
            product_and_price = product_and_price + "*Test*:%20" + data.product_id.name + "%0A" + \
                "*Price*:%20" + str(data.price) + \
                str(self.currency_id.symbol) + "%0A" + \
                "____________    %0A%0A"

        total_amount = "*Total Amount*: %20" + \
            str(self.amount_total) + str(self.currency_id.symbol) + "%0A%0A"

        text2 = "Do not hesitate to contact us if you have any questions."
        text2 += "%0A%0AClick here to download report %0A%0A"
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')

        text2 += base_url+self.get_download_report_url()

        url = "https://web.whatsapp.com/send?l=&phone="

        return {
            'type': 'ir.actions.act_url',
            'url': url + str(phone)+"&text=" + name + text + product_and_price + total_amount + text2,
            'target': 'new',
            # 'res_id': rec.id,
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update(
                {'name': self.env['ir.sequence'].next_by_code('appointment.entry')})
        return super(Appointment, self).create(vals_list)

    @api.depends('request_line', 'request_line.price')
    def _amount_untaxed_compute(self):
        for rec in self:
            rec.amount_untaxed = 0
            for product_id_obj in rec.request_line:
                rec.amount_untaxed = rec.amount_untaxed + product_id_obj.price

    @api.depends('request_line', 'request_line.tax_ids')
    def _amount_tax_compute(self):
        for rec in self:
            rec.amount_tax = 0
            for product_id_obj in rec.request_line:
                rec.amount_tax = rec.amount_tax+product_id_obj.price_tax

    @api.depends('amount_untaxed', 'amount_tax')
    def _amount_total_compute(self):
        for rec in self:
            rec.amount_total = rec.amount_untaxed+rec.amount_tax

    # Button Actions Starts

    def set_done(self):
        self.write({
            'state_type': 'done'
        })

    def set_cancel(self):
        self.write({
            'state_type': 'cancel'
        })

    def set_new(self):
        self.write({
            'state_type': 'new'
        })

    @api.onchange('technician_id')
    def onchange_technician_id(self):
        self.request_line.update({
            'technician_id': self.technician_id
        })

    def get_total_of_diagnosis(self):
        for rec in self:
            lines = self.env['sh.patho.request.line'].search(
                [('patient_details_id.name', '=', self.patient_id.name)])
            total_diagnosis = len(lines.ids)
            rec.total_diagnosis = total_diagnosis

    def def_open_diagnosis(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Diagnosis',
            'view_mode': 'tree,form',
            'res_model': 'sh.patho.request.line',
            'domain': [('patient_details_id.name', '=', self.patient_id.name)],
        }

    @api.onchange('lab_center_id')
    def _onchange_lab_center_id(self):
        if self.lab_center_id and self.lab_center_id != self.collection_center_id.laboratory_id:
            self.collection_center_id = False

    @api.onchange('collection_center_id')
    def _onchange_collection_center_id(self):
        if self.collection_center_id.laboratory_id:
            self.lab_center_id = self.collection_center_id.laboratory_id
