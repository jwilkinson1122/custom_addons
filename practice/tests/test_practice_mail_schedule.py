# -*- coding: utf-8 -*-


from datetime import datetime
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.addons.practice.tests.common import TestPracticeCommon
from odoo.addons.mail.tests.common import MockEmail
from odoo.tools import formataddr, mute_logger


class TestMailSchedule(TestPracticeCommon, MockEmail):

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_practice_mail_schedule(self):
        """ Test mail scheduling for practices """
        practice_cron_id = self.env.ref('practice.practice_mail_scheduler')

        # deactivate other schedulers to avoid messing with crons
        self.env['practice.mail'].search([]).unlink()

        # freeze some datetimes, and ensure more than 1D+1H before practice starts
        # to ease time-based scheduler check
        now = datetime(2021, 3, 20, 14, 30, 15)
        practice_date_begin = datetime(2021, 3, 22, 8, 0, 0)
        practice_date_end = datetime(2021, 3, 24, 18, 0, 0)

        with freeze_time(now):
            # create with admin to force create_date
            test_practice = self.env['practice.practice'].create({
                'name': 'TestPracticeMail',
                'create_date': now,
                'user_id': self.user_practicemanager.id,
                'auto_confirm': True,
                'date_begin': practice_date_begin,
                'date_end': practice_date_end,
                'practice_mail_ids': [
                    (0, 0, {  # right at subscription
                        'interval_unit': 'now',
                        'interval_type': 'after_sub',
                        'template_ref': 'mail.template,%i' % self.env['ir.model.data']._xmlid_to_res_id('practice.practice_subscription')}),
                    (0, 0, {  # one day after subscription
                        'interval_nbr': 1,
                        'interval_unit': 'hours',
                        'interval_type': 'after_sub',
                        'template_ref': 'mail.template,%i' % self.env['ir.model.data']._xmlid_to_res_id('practice.practice_subscription')}),
                    (0, 0, {  # 1 days before practice
                        'interval_nbr': 1,
                        'interval_unit': 'days',
                        'interval_type': 'before_practice',
                        'template_ref': 'mail.template,%i' % self.env['ir.model.data']._xmlid_to_res_id('practice.practice_reminder')}),
                    (0, 0, {  # immediately after practice
                        'interval_nbr': 1,
                        'interval_unit': 'hours',
                        'interval_type': 'after_practice',
                        'template_ref': 'mail.template,%i' % self.env['ir.model.data']._xmlid_to_res_id('practice.practice_reminder')}),
                ]
            })
            self.assertEqual(test_practice.create_date, now)

        # check subscription scheduler
        after_sub_scheduler = self.env['practice.mail'].search([('practice_id', '=', test_practice.id), ('interval_type', '=', 'after_sub'), ('interval_unit', '=', 'now')])
        self.assertEqual(len(after_sub_scheduler), 1, 'practice: wrong scheduler creation')
        self.assertEqual(after_sub_scheduler.scheduled_date, test_practice.create_date)
        self.assertFalse(after_sub_scheduler.mail_done)
        self.assertEqual(after_sub_scheduler.mail_state, 'running')
        self.assertEqual(after_sub_scheduler.mail_count_done, 0)
        after_sub_scheduler_2 = self.env['practice.mail'].search([('practice_id', '=', test_practice.id), ('interval_type', '=', 'after_sub'), ('interval_unit', '=', 'hours')])
        self.assertEqual(len(after_sub_scheduler_2), 1, 'practice: wrong scheduler creation')
        self.assertEqual(after_sub_scheduler_2.scheduled_date, test_practice.create_date + relativedelta(hours=1))
        self.assertFalse(after_sub_scheduler_2.mail_done)
        self.assertEqual(after_sub_scheduler_2.mail_state, 'running')
        self.assertEqual(after_sub_scheduler_2.mail_count_done, 0)
        # check before practice scheduler
        practice_prev_scheduler = self.env['practice.mail'].search([('practice_id', '=', test_practice.id), ('interval_type', '=', 'before_practice')])
        self.assertEqual(len(practice_prev_scheduler), 1, 'practice: wrong scheduler creation')
        self.assertEqual(practice_prev_scheduler.scheduled_date, practice_date_begin + relativedelta(days=-1))
        self.assertFalse(practice_prev_scheduler.mail_done)
        self.assertEqual(practice_prev_scheduler.mail_state, 'scheduled')
        self.assertEqual(practice_prev_scheduler.mail_count_done, 0)
        # check after practice scheduler
        practice_next_scheduler = self.env['practice.mail'].search([('practice_id', '=', test_practice.id), ('interval_type', '=', 'after_practice')])
        self.assertEqual(len(practice_next_scheduler), 1, 'practice: wrong scheduler creation')
        self.assertEqual(practice_next_scheduler.scheduled_date, practice_date_end + relativedelta(hours=1))
        self.assertFalse(practice_next_scheduler.mail_done)
        self.assertEqual(practice_next_scheduler.mail_state, 'scheduled')
        self.assertEqual(practice_next_scheduler.mail_count_done, 0)

        # create some confirmations
        with freeze_time(now), self.mock_mail_gateway():
            reg1 = self.env['practice.confirmation'].with_user(self.user_practiceuser).create({
                'practice_id': test_practice.id,
                'name': 'Reg1',
                'email': 'reg1@example.com',
            })
            reg2 = self.env['practice.confirmation'].with_user(self.user_practiceuser).create({
                'practice_id': test_practice.id,
                'name': 'Reg2',
                'email': 'reg2@example.com',
            })

        # REGISTRATIONS / PRE SCHEDULERS
        # --------------------------------------------------

        # check confirmation state
        self.assertTrue(all(reg.state == 'open' for reg in reg1 + reg2), 'Confirmations: should be auto-confirmed')
        self.assertTrue(all(reg.date_open == now for reg in reg1 + reg2), 'Confirmations: should have open date set to confirm date')

        # verify that subscription scheduler was auto-executed after each confirmation
        self.assertEqual(len(after_sub_scheduler.mail_confirmation_ids), 2, 'practice: should have 2 scheduled communication (1 / confirmation)')
        for mail_confirmation in after_sub_scheduler.mail_confirmation_ids:
            self.assertEqual(mail_confirmation.scheduled_date, now)
            self.assertTrue(mail_confirmation.mail_sent, 'practice: confirmation mail should be sent at confirmation creation')
        self.assertTrue(after_sub_scheduler.mail_done, 'practice: all subscription mails should have been sent')
        self.assertEqual(after_sub_scheduler.mail_state, 'running')
        self.assertEqual(after_sub_scheduler.mail_count_done, 2)

        # check emails effectively sent
        self.assertEqual(len(self._new_mails), 2, 'practice: should have 2 scheduled emails (1 / confirmation)')
        self.assertMailMailWEmails(
            [formataddr((reg1.name, reg1.email)), formataddr((reg2.name, reg2.email))],
            'outgoing',
            content=None,
            fields_values={'subject': 'Your confirmation at %s' % test_practice.name,
                           'email_from': self.user_practicemanager.company_id.email_formatted,
                          })

        # same for second scheduler: scheduled but not sent
        self.assertEqual(len(after_sub_scheduler_2.mail_confirmation_ids), 2, 'practice: should have 2 scheduled communication (1 / confirmation)')
        for mail_confirmation in after_sub_scheduler_2.mail_confirmation_ids:
            self.assertEqual(mail_confirmation.scheduled_date, now + relativedelta(hours=1))
            self.assertFalse(mail_confirmation.mail_sent, 'practice: confirmation mail should be scheduled, not sent')
        self.assertFalse(after_sub_scheduler_2.mail_done, 'practice: all subscription mails should be scheduled, not sent')
        self.assertEqual(after_sub_scheduler_2.mail_count_done, 0)

        # execute practice reminder scheduler explicitly, before scheduled date -> should not do anything
        with freeze_time(now), self.mock_mail_gateway():
            after_sub_scheduler_2.execute()
        self.assertFalse(any(mail_reg.mail_sent for mail_reg in after_sub_scheduler_2.mail_confirmation_ids))
        self.assertFalse(after_sub_scheduler_2.mail_done)
        self.assertEqual(after_sub_scheduler_2.mail_count_done, 0)
        self.assertEqual(len(self._new_mails), 0, 'practice: should not send mails before scheduled date')

        # execute practice reminder scheduler explicitly, right at scheduled date -> should sent mails
        now_confirmation = now + relativedelta(hours=1)
        with freeze_time(now_confirmation), self.mock_mail_gateway():
            after_sub_scheduler_2.execute()

        # verify that subscription scheduler was auto-executed after each confirmation
        self.assertEqual(len(after_sub_scheduler_2.mail_confirmation_ids), 2, 'practice: should have 2 scheduled communication (1 / confirmation)')
        self.assertTrue(all(mail_reg.mail_sent for mail_reg in after_sub_scheduler_2.mail_confirmation_ids))
        self.assertTrue(after_sub_scheduler_2.mail_done, 'practice: all subscription mails should have been sent')
        self.assertEqual(after_sub_scheduler_2.mail_state, 'running')
        self.assertEqual(after_sub_scheduler_2.mail_count_done, 2)

        # check emails effectively sent
        self.assertEqual(len(self._new_mails), 2, 'practice: should have 2 scheduled emails (1 / confirmation)')
        self.assertMailMailWEmails(
            [formataddr((reg1.name, reg1.email)), formataddr((reg2.name, reg2.email))],
            'outgoing',
            content=None,
            fields_values={'subject': 'Your confirmation at %s' % test_practice.name,
                           'email_from': self.user_practicemanager.company_id.email_formatted,
                          })

        # PRE SCHEDULERS (MOVE FORWARD IN TIME)
        # --------------------------------------------------

        self.assertFalse(practice_prev_scheduler.mail_done)
        self.assertEqual(practice_prev_scheduler.mail_state, 'scheduled')

        # simulate cron running before scheduled date -> should not do anything
        now_start = practice_date_begin + relativedelta(hours=-25)
        with freeze_time(now_start), self.mock_mail_gateway():
            practice_cron_id.method_direct_trigger()

        self.assertFalse(practice_prev_scheduler.mail_done)
        self.assertEqual(practice_prev_scheduler.mail_state, 'scheduled')
        self.assertEqual(practice_prev_scheduler.mail_count_done, 0)
        self.assertEqual(len(self._new_mails), 0)

        # execute cron to run schedulers after scheduled date
        now_start = practice_date_begin + relativedelta(hours=-23)
        with freeze_time(now_start), self.mock_mail_gateway():
            practice_cron_id.method_direct_trigger()

        # check that scheduler is finished
        self.assertTrue(practice_prev_scheduler.mail_done, 'practice: reminder scheduler should have run')
        self.assertEqual(practice_prev_scheduler.mail_state, 'sent', 'practice: reminder scheduler should have run')

        # check emails effectively sent
        self.assertEqual(len(self._new_mails), 2, 'practice: should have scheduled 2 mails (1 / confirmation)')
        self.assertMailMailWEmails(
            [formataddr((reg1.name, reg1.email)), formataddr((reg2.name, reg2.email))],
            'outgoing',
            content=None,
            fields_values={'subject': '%s: tomorrow' % test_practice.name,
                           'email_from': self.user_practicemanager.company_id.email_formatted,
                          })

        # NEW REGISTRATION EFFECT ON SCHEDULERS
        # --------------------------------------------------

        test_practice.write({'auto_confirm': False})
        with freeze_time(now_start), self.mock_mail_gateway():
            reg3 = self.env['practice.confirmation'].with_user(self.user_practiceuser).create({
                'practice_id': test_practice.id,
                'name': 'Reg3',
                'email': 'reg3@example.com',
            })

        # no more seats
        self.assertEqual(reg3.state, 'draft')

        # schedulers state untouched
        self.assertTrue(practice_prev_scheduler.mail_done)
        self.assertFalse(practice_next_scheduler.mail_done)
        self.assertTrue(after_sub_scheduler.mail_done, 'practice: scheduler on confirmation not updated next to draft confirmation')
        self.assertTrue(after_sub_scheduler_2.mail_done, 'practice: scheduler on confirmation not updated next to draft confirmation')

        # confirm confirmation -> should trigger confirmation schedulers
        # NOTE: currently all schedulers are based on date_open which equals create_date
        # meaning several communications may be sent in the time time
        with freeze_time(now_start + relativedelta(hours=1)), self.mock_mail_gateway():
            reg3.action_confirm()

        # verify that subscription scheduler was auto-executed after new confirmation confirmed
        self.assertEqual(len(after_sub_scheduler.mail_confirmation_ids), 3, 'practice: should have 3 scheduled communication (1 / confirmation)')
        new_mail_reg = after_sub_scheduler.mail_confirmation_ids.filtered(lambda mail_reg: mail_reg.confirmation_id == reg3)
        self.assertEqual(new_mail_reg.scheduled_date, now_start)
        self.assertTrue(new_mail_reg.mail_sent, 'practice: confirmation mail should be sent at confirmation creation')
        self.assertTrue(after_sub_scheduler.mail_done, 'practice: all subscription mails should have been sent')
        self.assertEqual(after_sub_scheduler.mail_count_done, 3)
        # verify that subscription scheduler was auto-executed after new confirmation confirmed
        self.assertEqual(len(after_sub_scheduler_2.mail_confirmation_ids), 3, 'practice: should have 3 scheduled communication (1 / confirmation)')
        new_mail_reg = after_sub_scheduler_2.mail_confirmation_ids.filtered(lambda mail_reg: mail_reg.confirmation_id == reg3)
        self.assertEqual(new_mail_reg.scheduled_date, now_start + relativedelta(hours=1))
        self.assertTrue(new_mail_reg.mail_sent, 'practice: confirmation mail should be sent at confirmation creation')
        self.assertTrue(after_sub_scheduler_2.mail_done, 'practice: all subscription mails should have been sent')
        self.assertEqual(after_sub_scheduler_2.mail_count_done, 3)

        # check emails effectively sent
        self.assertEqual(len(self._new_mails), 2, 'practice: should have 1 scheduled emails (new confirmation only)')
        # manual check because 2 identical mails are sent and mail tools do not support it easily
        for mail in self._new_mails:
            self.assertEqual(mail.email_from, self.user_practicemanager.company_id.email_formatted)
            self.assertEqual(mail.subject, 'Your confirmation at %s' % test_practice.name)
            self.assertEqual(mail.state, 'outgoing')
            self.assertEqual(mail.email_to, formataddr((reg3.name, reg3.email)))

        # POST SCHEDULERS (MOVE FORWARD IN TIME)
        # --------------------------------------------------

        self.assertFalse(practice_next_scheduler.mail_done)

        # execute practice reminder scheduler explicitly after its schedule date
        new_end = practice_date_end + relativedelta(hours=2)
        with freeze_time(new_end), self.mock_mail_gateway():
            practice_cron_id.method_direct_trigger()

        # check that scheduler is finished
        self.assertTrue(practice_next_scheduler.mail_done, 'practice: reminder scheduler should should have run')
        self.assertEqual(practice_next_scheduler.mail_state, 'sent', 'practice: reminder scheduler should have run')
        self.assertEqual(practice_next_scheduler.mail_count_done, 3)

        # check emails effectively sent
        self.assertEqual(len(self._new_mails), 3, 'practice: should have scheduled 3 mails, one for each confirmation')
        self.assertMailMailWEmails(
            [formataddr((reg1.name, reg1.email)), formataddr((reg2.name, reg2.email)), formataddr((reg3.name, reg3.email))],
            'outgoing',
            content=None,
            fields_values={'subject': '%s: today' % test_practice.name,
                           'email_from': self.user_practicemanager.company_id.email_formatted,
                          })
