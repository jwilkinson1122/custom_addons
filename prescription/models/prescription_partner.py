

import math
import pytz

from datetime import datetime, time, timedelta
from textwrap import dedent

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import float_round

from odoo.addons.base.models.res_partner import _tz_get


WEEKDAY_TO_NAME = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
CRON_DEPENDS = {'name', 'active', 'send_by', 'automatic_email_time', 'moment', 'tz'}

def float_to_time(hours, moment='am'):
    """ Convert a number of hours into a time object. """
    if hours == 12.0 and moment == 'pm':
        return time.max
    fractional, integral = math.modf(hours)
    if moment == 'pm':
        integral += 12
    return time(int(integral), int(float_round(60 * fractional, precision_digits=0)), 0)

def time_to_float(t):
    return float_round(t.hour + t.minute/60 + t.second/3600, precision_digits=2)

class PrescriptionPartner(models.Model):
    _name = 'prescription.partner'
    _description = 'Prescription Partner'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)

    name = fields.Char('Name', related='partner_id.name', readonly=False)

    email = fields.Char(related='partner_id.email', readonly=False)
    email_formatted = fields.Char(related='partner_id.email_formatted', readonly=True)
    phone = fields.Char(related='partner_id.phone', readonly=False)
    street = fields.Char(related='partner_id.street', readonly=False)
    street2 = fields.Char(related='partner_id.street2', readonly=False)
    zip_code = fields.Char(related='partner_id.zip', readonly=False)
    city = fields.Char(related='partner_id.city', readonly=False)
    state_id = fields.Many2one("res.country.state", related='partner_id.state_id', readonly=False)
    country_id = fields.Many2one('res.country', related='partner_id.country_id', readonly=False)
    company_id = fields.Many2one('res.company', related='partner_id.company_id', readonly=False, store=True)

    responsible_id = fields.Many2one('res.users', string="Responsible", domain=lambda self: [('groups_id', 'in', self.env.ref('prescription.group_prescription_manager').id)],
                                     default=lambda self: self.env.user,
                                     help="The responsible is the person that will order prescription for everyone. It will be used as the 'from' when sending the automatic email.")

    send_by = fields.Selection([
        ('phone', 'Phone'),
        ('mail', 'Email'),
    ], 'Send Order By', default='phone')
    automatic_email_time = fields.Float('Order Time', default=12.0, required=True)
    cron_id = fields.Many2one('ir.cron', ondelete='cascade', required=True, readonly=True)

    mon = fields.Boolean(default=True)
    tue = fields.Boolean(default=True)
    wed = fields.Boolean(default=True)
    thu = fields.Boolean(default=True)
    fri = fields.Boolean(default=True)
    sat = fields.Boolean()
    sun = fields.Boolean()

    recurrency_end_date = fields.Date('Until', help="This field is used in order to ")

    available_location_ids = fields.Many2many('prescription.location', string='Location')
    available_today = fields.Boolean('This is True when if the partner is available today',
                                     compute='_compute_available_today', search='_search_available_today')

    tz = fields.Selection(_tz_get, string='Timezone', required=True, default=lambda self: self.env.user.tz or 'UTC')

    active = fields.Boolean(default=True)

    moment = fields.Selection([
        ('am', 'AM'),
        ('pm', 'PM'),
    ], default='am', required=True)

    delivery = fields.Selection([
        ('delivery', 'Delivery'),
        ('no_delivery', 'No Delivery')
    ], default='no_delivery')

    option_label_1 = fields.Char('Extra 1 Label', required=True, default='Extras')
    option_label_2 = fields.Char('Extra 2 Label', required=True, default='Beverages')
    option_label_3 = fields.Char('Extra 3 Label', required=True, default='Extra Label 3')
    option_ids_1 = fields.One2many('prescription.option', 'partner_id', domain=[('option_category', '=', 1)])
    option_ids_2 = fields.One2many('prescription.option', 'partner_id', domain=[('option_category', '=', 2)])
    option_ids_3 = fields.One2many('prescription.option', 'partner_id', domain=[('option_category', '=', 3)])
    option_quantity_1 = fields.Selection([
        ('0_more', 'None or More'),
        ('1_more', 'One or More'),
        ('1', 'Only One')], 'Extra 1 Quantity', default='0_more', required=True)
    option_quantity_2 = fields.Selection([
        ('0_more', 'None or More'),
        ('1_more', 'One or More'),
        ('1', 'Only One')], 'Extra 2 Quantity', default='0_more', required=True)
    option_quantity_3 = fields.Selection([
        ('0_more', 'None or More'),
        ('1_more', 'One or More'),
        ('1', 'Only One')], 'Extra 3 Quantity', default='0_more', required=True)

    _sql_constraints = [
        ('automatic_email_time_range',
         'CHECK(automatic_email_time >= 0 AND automatic_email_time <= 12)',
         'Automatic Email Sending Time should be between 0 and 12'),
    ]

    def name_get(self):
        res = []
        for partner in self:
            if partner.phone:
                res.append((partner.id, '%s %s' % (partner.name, partner.phone)))
            else:
                res.append((partner.id, partner.name))
        return res

    def _sync_cron(self):
        for partner in self:
            partner = partner.with_context(tz=partner.tz)

            sendat_tz = pytz.timezone(partner.tz).localize(datetime.combine(
                fields.Date.context_today(partner),
                float_to_time(partner.automatic_email_time, partner.moment)))
            cron = partner.cron_id.sudo()
            lc = cron.lastcall
            if ((
                lc and sendat_tz.date() <= fields.Datetime.context_timestamp(partner, lc).date()
            ) or (
                not lc and sendat_tz <= fields.Datetime.context_timestamp(partner, fields.Datetime.now())
            )):
                sendat_tz += timedelta(days=1)
            sendat_utc = sendat_tz.astimezone(pytz.UTC).replace(tzinfo=None)

            cron.active = partner.active and partner.send_by == 'mail'
            cron.name = f"Prescription: send automatic email to {partner.name}"
            cron.nextcall = sendat_utc
            cron.code = dedent(f"""\
                # This cron is dynamically controlled by {self._description}.
                # Do NOT modify this cron, modify the related record instead.
                env['{self._name}'].browse([{partner.id}])._send_auto_email()""")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            for option in vals.get('option_ids_2', []):
                option[2].update({'option_category': 2})
            for option in vals.get('option_ids_3', []):
                option[2].update({'option_category': 3})
        crons = self.env['ir.cron'].sudo().create([
            {
                'user_id': self.env.ref('base.user_root').id,
                'active': False,
                'interval_type': 'days',
                'interval_number': 1,
                'numbercall': -1,
                'doall': False,
                'name': "Prescription: send automatic email",
                'model_id': self.env['ir.model']._get_id(self._name),
                'state': 'code',
                'code': "",
            }
            for _ in range(len(vals_list))
        ])
        self.env['ir.model.data'].sudo().create([{
            'name': f'prescription_partner_cron_sa_{cron.ir_actions_server_id.id}',
            'module': 'prescription',
            'res_id': cron.ir_actions_server_id.id,
            'model': 'ir.actions.server',
            # noupdate is set to true to avoid to delete record at module update
            'noupdate': True,
        } for cron in crons])
        for vals, cron in zip(vals_list, crons):
            vals['cron_id'] = cron.id

        partners = super().create(vals_list)
        partners._sync_cron()
        return partners

    def write(self, values):
        for option in values.get('option_ids_2', []):
            option_values = option[2]
            if option_values:
                option_values.update({'option_category': 2})
        for option in values.get('option_ids_3', []):
            option_values = option[2]
            if option_values:
                option_values.update({'option_category': 3})
        if values.get('company_id'):
            self.env['prescription.order'].search([('partner_id', 'in', self.ids)]).write({'company_id': values['company_id']})
        super().write(values)
        if not CRON_DEPENDS.isdisjoint(values):
            self._sync_cron()

    def unlink(self):
        crons = self.cron_id.sudo()
        server_actions = crons.ir_actions_server_id
        super().unlink()
        crons.unlink()
        server_actions.unlink()

    def toggle_active(self):
        """ Archiving related prescription product """
        res = super().toggle_active()
        active_partners = self.filtered(lambda s: s.active)
        inactive_partners = self - active_partners
        Product = self.env['prescription.product'].with_context(active_test=False)
        Product.search([('partner_id', 'in', active_partners.ids)]).write({'active': True})
        Product.search([('partner_id', 'in', inactive_partners.ids)]).write({'active': False})
        return res

    def _send_auto_email(self):
        """ Send an email to the partner with the order of the day """
        # Called daily by cron
        self.ensure_one()

        if not self.available_today:
            return

        if self.send_by != 'mail':
            raise ValueError("Cannot send an email to this partner")

        orders = self.env['prescription.order'].search([
            ('partner_id', '=', self.id),
            ('state', '=', 'ordered'),
            ('date', '=', fields.Date.context_today(self.with_context(tz=self.tz))),
        ], order="user_id, name")
        if not orders:
            return

        order = {
            'company_name': orders[0].company_id.name,
            'currency_id': orders[0].currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_name': self.name,
            'email_from': self.responsible_id.email_formatted,
            'amount_total': sum(order.price for order in orders),
        }

        sites = orders.mapped('user_id.last_prescription_location_id').sorted(lambda x: x.name)
        orders_per_site = orders.sorted(lambda x: x.user_id.last_prescription_location_id.id)

        email_orders = [{
            'product': order.product_id.name,
            'note': order.note,
            'quantity': order.quantity,
            'price': order.price,
            'options': order.display_options,
            'username': order.user_id.name,
            'site': order.user_id.last_prescription_location_id.name,
        } for order in orders_per_site]

        email_sites = [{
            'name': site.name,
            'address': site.address,
        } for site in sites]

        self.env.ref('prescription.prescription_order_mail_partner').with_context(
            order=order, lines=email_orders, sites=email_sites
        ).send_mail(self.id)

        orders.action_confirm()

    @api.depends('recurrency_end_date', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')
    def _compute_available_today(self):
        now = fields.Datetime.now().replace(tzinfo=pytz.UTC)

        for partner in self:
            now = now.astimezone(pytz.timezone(partner.tz))

            if partner.recurrency_end_date and now.date() >= partner.recurrency_end_date:
                partner.available_today = False
            else:
                fieldname = WEEKDAY_TO_NAME[now.weekday()]
                partner.available_today = partner[fieldname]

    def _search_available_today(self, operator, value):
        if (not operator in ['=', '!=']) or (not value in [True, False]):
            return []

        searching_for_true = (operator == '=' and value) or (operator == '!=' and not value)

        now = fields.Datetime.now().replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(self.env.user.tz or 'UTC'))
        fieldname = WEEKDAY_TO_NAME[now.weekday()]

        recurrency_domain = expression.OR([
            [('recurrency_end_date', '=', False)],
            [('recurrency_end_date', '>' if searching_for_true else '<', now)]
        ])

        return expression.AND([
            recurrency_domain,
            [(fieldname, operator, value)]
        ])
