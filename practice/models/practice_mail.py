# -*- coding: utf-8 -*-


import logging
import random
import threading

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools
from odoo.tools import exception_to_unicode
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

_INTERVALS = {
    'hours': lambda interval: relativedelta(hours=interval),
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'now': lambda interval: relativedelta(hours=0),
}


class PracticeTypeMail(models.Model):
    """ Template of practice.mail to attach to practice.type. Those will be copied
    upon all practices created in that type to ease practice creation. """
    _name = 'practice.type.mail'
    _description = 'Mail Scheduling on Practice Category'

    @api.model
    def _selection_template_model(self):
        return [('mail.template', 'Mail')]

    practice_type_id = fields.Many2one(
        'practice.type', string='Practice Type',
        ondelete='cascade', required=True)
    notification_type = fields.Selection([('mail', 'Mail')], string='Send', default='mail', required=True)
    interval_nbr = fields.Integer('Interval', default=1)
    interval_unit = fields.Selection([
        ('now', 'Immediately'),
        ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')],
        string='Unit', default='hours', required=True)
    interval_type = fields.Selection([
        ('after_sub', 'After each confirmation'),
        ('before_practice', 'Before the practice'),
        ('after_practice', 'After the practice')],
        string='Trigger', default="before_practice", required=True)
    template_model_id = fields.Many2one('ir.model', string='Template Model', compute='_compute_template_model_id', compute_sudo=True)
    template_ref = fields.Reference(string='Template', selection='_selection_template_model', required=True)

    @api.depends('notification_type')
    def _compute_template_model_id(self):
        mail_model = self.env['ir.model']._get('mail.template')
        for mail in self:
            mail.template_model_id = mail_model if mail.notification_type == 'mail' else False

    def _prepare_practice_mail_values(self):
        self.ensure_one()
        return {
            'notification_type': self.notification_type,
            'interval_nbr': self.interval_nbr,
            'interval_unit': self.interval_unit,
            'interval_type': self.interval_type,
            'template_ref': '%s,%i' % (self.template_ref._name, self.template_ref.id)
        }


class PracticeMailScheduler(models.Model):
    """ Practice automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on practices since Odoo 9. A cron exists
    that periodically checks for mailing to run. """
    _name = 'practice.mail'
    _rec_name = 'practice_id'
    _description = 'Practice Automated Mailing'

    @api.model
    def _selection_template_model(self):
        return [('mail.template', 'Mail')]

    practice_id = fields.Many2one('practice.practice', string='Practice', required=True, ondelete='cascade')
    sequence = fields.Integer('Display order')
    notification_type = fields.Selection([('mail', 'Mail')], string='Send', default='mail', required=True)
    interval_nbr = fields.Integer('Interval', default=1)
    interval_unit = fields.Selection([
        ('now', 'Immediately'),
        ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')],
        string='Unit', default='hours', required=True)
    interval_type = fields.Selection([
        ('after_sub', 'After each confirmation'),
        ('before_practice', 'Before the practice'),
        ('after_practice', 'After the practice')],
        string='Trigger ', default="before_practice", required=True)
    scheduled_date = fields.Datetime('Schedule Date', compute='_compute_scheduled_date', store=True)
    # contact and status
    mail_confirmation_ids = fields.One2many(
        'practice.mail.confirmation', 'scheduler_id',
        help='Communication related to practice confirmations')
    mail_done = fields.Boolean("Sent", copy=False, readonly=True)
    mail_state = fields.Selection(
        [('running', 'Running'), ('scheduled', 'Scheduled'), ('sent', 'Sent')],
        string='Global communication Status', compute='_compute_mail_state')
    mail_count_done = fields.Integer('# Sent', copy=False, readonly=True)
    template_model_id = fields.Many2one('ir.model', string='Template Model', compute='_compute_template_model_id', compute_sudo=True)
    template_ref = fields.Reference(string='Template', selection='_selection_template_model', required=True)

    @api.depends('notification_type')
    def _compute_template_model_id(self):
        mail_model = self.env['ir.model']._get('mail.template')
        for mail in self:
            mail.template_model_id = mail_model if mail.notification_type == 'mail' else False

    @api.depends('practice_id.date_begin', 'practice_id.date_end', 'interval_type', 'interval_unit', 'interval_nbr')
    def _compute_scheduled_date(self):
        for scheduler in self:
            if scheduler.interval_type == 'after_sub':
                date, sign = scheduler.practice_id.create_date, 1
            elif scheduler.interval_type == 'before_practice':
                date, sign = scheduler.practice_id.date_begin, -1
            else:
                date, sign = scheduler.practice_id.date_end, 1

            scheduler.scheduled_date = date + _INTERVALS[scheduler.interval_unit](sign * scheduler.interval_nbr) if date else False

    @api.depends('interval_type', 'scheduled_date', 'mail_done')
    def _compute_mail_state(self):
        for scheduler in self:
            # confirmations based
            if scheduler.interval_type == 'after_sub':
                scheduler.mail_state = 'running'
            # global practice based
            elif scheduler.mail_done:
                scheduler.mail_state = 'sent'
            elif scheduler.scheduled_date:
                scheduler.mail_state = 'scheduled'
            else:
                scheduler.mail_state = 'running'

    def execute(self):
        for scheduler in self:
            now = fields.Datetime.now()
            if scheduler.interval_type == 'after_sub':
                new_confirmations = scheduler.practice_id.confirmation_ids.filtered_domain(
                    [('state', 'not in', ('cancel', 'draft'))]
                ) - scheduler.mail_confirmation_ids.confirmation_id
                scheduler._create_missing_mail_confirmations(new_confirmations)

                # execute scheduler on confirmations
                scheduler.mail_confirmation_ids.execute()
                total_sent = len(scheduler.mail_confirmation_ids.filtered(lambda reg: reg.mail_sent))
                scheduler.update({
                    'mail_done': total_sent >= (scheduler.practice_id.seats_reserved + scheduler.practice_id.seats_used),
                    'mail_count_done': total_sent,
                })
            else:
                # before or after practice -> one shot email
                if scheduler.mail_done or scheduler.notification_type != 'mail':
                    continue
                # no template -> ill configured, skip and avoid crash
                if not scheduler.template_ref:
                    continue
                # do not send emails if the mailing was scheduled before the practice but the practice is over
                if scheduler.scheduled_date <= now and (scheduler.interval_type != 'before_practice' or scheduler.practice_id.date_end > now):
                    scheduler.practice_id.mail_attendees(scheduler.template_ref.id)
                    scheduler.update({
                        'mail_done': True,
                        'mail_count_done': scheduler.practice_id.seats_reserved + scheduler.practice_id.seats_used,
                    })
        return True

    def _create_missing_mail_confirmations(self, confirmations):
        new = []
        for scheduler in self:
            new += [{
                'confirmation_id': confirmation.id,
                'scheduler_id': scheduler.id,
            } for confirmation in confirmations]
        if new:
            return self.env['practice.mail.confirmation'].create(new)
        return self.env['practice.mail.confirmation']

    @api.model
    def _warn_template_error(self, scheduler, exception):
        # We warn ~ once by hour ~ instead of every 10 min if the interval unit is more than 'hours'.
        if random.random() < 0.1666 or scheduler.interval_unit in ('now', 'hours'):
            ex_s = exception_to_unicode(exception)
            try:
                practice, template = scheduler.practice_id, scheduler.template_ref
                emails = list(set([practice.organizer_id.email, practice.user_id.email, template.write_uid.email]))
                subject = _("WARNING: Practice Scheduler Error for practice: %s", practice.name)
                body = _("""Practice Scheduler for:
  - Practice: %(practice_name)s (%(practice_id)s)
  - Scheduled: %(date)s
  - Template: %(template_name)s (%(template_id)s)

Failed with error:
  - %(error)s

You receive this email because you are:
  - the organizer of the practice,
  - or the responsible of the practice,
  - or the last writer of the template.
""",
                         practice_name=practice.name,
                         practice_id=practice.id,
                         date=scheduler.scheduled_date,
                         template_name=template.name,
                         template_id=template.id,
                         error=ex_s)
                email = self.env['ir.mail_server'].build_email(
                    email_from=self.env.user.email,
                    email_to=emails,
                    subject=subject, body=body,
                )
                self.env['ir.mail_server'].send_email(email)
            except Exception as e:
                _logger.error("Exception while sending traceback by email: %s.\n Original Traceback:\n%s", e, exception)
                pass

    @api.model
    def run(self, autocommit=False):
        """ Backward compatible method, notably if crons are not updated when
        migrating for some reason. """
        return self.schedule_communications(autocommit=autocommit)

    @api.model
    def schedule_communications(self, autocommit=False):
        schedulers = self.search([
            ('mail_done', '=', False),
            ('scheduled_date', '<=', fields.Datetime.now())
        ])

        for scheduler in schedulers:
            try:
                # Prpractice a mega prefetch of the confirmation ids of all the practices of all the schedulers
                self.browse(scheduler.id).execute()
            except Exception as e:
                _logger.exception(e)
                self.invalidate_cache()
                self._warn_template_error(scheduler, e)
            else:
                if autocommit and not getattr(threading.current_thread(), 'testing', False):
                    self.env.cr.commit()
        return True


class PracticeMailConfirmation(models.Model):
    _name = 'practice.mail.confirmation'
    _description = 'Confirmation Mail Scheduler'
    _rec_name = 'scheduler_id'
    _order = 'scheduled_date DESC'

    scheduler_id = fields.Many2one('practice.mail', 'Mail Scheduler', required=True, ondelete='cascade')
    confirmation_id = fields.Many2one('practice.confirmation', 'Attendee', required=True, ondelete='cascade')
    scheduled_date = fields.Datetime('Scheduled Time', compute='_compute_scheduled_date', store=True)
    mail_sent = fields.Boolean('Mail Sent')

    def execute(self):
        now = fields.Datetime.now()
        todo = self.filtered(lambda reg_mail:
            not reg_mail.mail_sent and \
            reg_mail.confirmation_id.state in ['open', 'done'] and \
            (reg_mail.scheduled_date and reg_mail.scheduled_date <= now) and \
            reg_mail.scheduler_id.notification_type == 'mail'
        )
        for reg_mail in todo:
            organizer = reg_mail.scheduler_id.practice_id.organizer_id
            company = self.env.company
            author = self.env.ref('base.user_root')
            if organizer.email:
                author = organizer
            elif company.email:
                author = company.partner_id
            elif self.env.user.email:
                author = self.env.user

            email_values = {
                'author_id': author.id,
            }
            if not reg_mail.scheduler_id.template_ref.email_from:
                email_values['email_from'] = author.email_formatted
            reg_mail.scheduler_id.template_ref.send_mail(reg_mail.confirmation_id.id, email_values=email_values)
        todo.write({'mail_sent': True})

    @api.depends('confirmation_id', 'scheduler_id.interval_unit', 'scheduler_id.interval_type')
    def _compute_scheduled_date(self):
        for mail in self:
            if mail.confirmation_id:
                date_open = mail.confirmation_id.date_open
                date_open_datetime = date_open or fields.Datetime.now()
                mail.scheduled_date = date_open_datetime + _INTERVALS[mail.scheduler_id.interval_unit](mail.scheduler_id.interval_nbr)
            else:
                mail.scheduled_date = False
