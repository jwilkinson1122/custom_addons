

import pytz

from datetime import datetime, time, timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests import common

from odoo.addons.prescription.tests.common import TestsCommon


class TestPartner(TestsCommon):
    def setUp(self):
        super(TestPartner, self).setUp()

        self.monday_1am = datetime(2018, 10, 29, 1, 0, 0)
        self.monday_10am = datetime(2018, 10, 29, 10, 0, 0)
        self.monday_1pm = datetime(2018, 10, 29, 13, 0, 0)
        self.monday_8pm = datetime(2018, 10, 29, 20, 0, 0)

        self.saturday_3am = datetime(2018, 11, 3, 3, 0, 0)
        self.saturday_10am = datetime(2018, 11, 3, 10, 0, 0)
        self.saturday_1pm = datetime(2018, 11, 3, 13, 0, 0)
        self.saturday_8pm = datetime(2018, 11, 3, 20, 0, 0)

    @common.users('cle-prescription-manager')
    def test_send_email_cron(self):
        self.partner_kothai.cron_id.ensure_one()
        self.assertEqual(self.partner_kothai.cron_id.nextcall.time(), time(15, 0))
        self.assertEqual(self.partner_kothai.cron_id.code, f"""\
# This cron is dynamically controlled by Prescription Partner.
# Do NOT modify this cron, modify the related record instead.
env['prescription.partner'].browse([{self.partner_kothai.id}])._send_auto_email()""")

        cron_id = self.partner_kothai.cron_id.id
        self.partner_kothai.unlink()
        self.assertFalse(self.env['ir.cron'].sudo().search([('id', '=', cron_id)]))

    @common.users('cle-prescription-manager')
    def test_compute_available_today(self):
        tests = [(self.monday_1am, True), (self.monday_10am, True),
                 (self.monday_1pm, True), (self.monday_8pm, True),
                 (self.saturday_3am, False), (self.saturday_10am, False),
                 (self.saturday_1pm, False), (self.saturday_8pm, False)]

        for value, result in tests:
            with patch.object(fields.Datetime, 'now', return_value=value) as _:
                assert self.partner_pizza_inn.available_today == result,\
                    'partner pizza inn should %s considered available on %s' % ('be' if result else 'not be', value)

            self.env['prescription.partner'].invalidate_cache(['available_today'], [self.partner_pizza_inn.id])

    @common.users('cle-prescription-manager')
    def test_search_available_today(self):
        '''
            This test checks that _search_available_today returns a valid domain
        '''
        self.env.user.tz = 'Europe/Brussels'
        Partner = self.env['prescription.partner']

        tests = [(self.monday_1am, 1.0, 'mon'), (self.monday_10am, 10.0, 'mon'),
                 (self.monday_1pm, 13.0, 'mon'), (self.monday_8pm, 20.0, 'mon'),
                 (self.saturday_3am, 3.0, 'sat'), (self.saturday_10am, 10.0, 'sat'),
                 (self.saturday_1pm, 13.0, 'sat'), (self.saturday_8pm, 20.0, 'sat')]

        # It should return an empty domain if we compare to values other than datetime
        assert Partner._search_available_today('>', 7) == []
        assert Partner._search_available_today('>', True) == []

        for value, rvalue, dayname in tests:
            with patch.object(fields.Datetime, 'now', return_value=value) as _:
                assert Partner._search_available_today('=', True) == ['&', '|', ('recurrency_end_date', '=', False),
                        ('recurrency_end_date', '>', value.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(self.env.user.tz))),
                        (dayname, '=', True)],\
                        'Wrong domain generated for values (%s, %s)' % (value, rvalue)

        with patch.object(fields.Datetime, 'now', return_value=self.monday_10am) as _:
            assert self.partner_pizza_inn in Partner.search([('available_today', '=', True)])

    @common.users('cle-prescription-manager')
    def test_auto_email_send(self):
        with patch.object(fields.Datetime, 'now', return_value=self.monday_1pm) as _:
            with patch.object(fields.Date, 'today', return_value=self.monday_1pm.date()) as _:
                with patch.object(fields.Date, 'context_today', return_value=self.monday_1pm.date()) as _:
                    line = self.env['prescription.order'].create({
                        'product_id': self.product_pizza.id,
                        'date': self.monday_1pm.date(),
                        'partner_id': self.partner_pizza_inn.id,
                    })

                    line.action_order()
                    assert line.state == 'ordered'

                    self.partner_pizza_inn._send_auto_email()

                    assert line.state == 'confirmed'

                    line = self.env['prescription.order'].create({
                        'product_id': self.product_pizza.id,
                        'option_ids_1': [(6, 0, [self.option_olives.id])],
                        'date': self.monday_1pm.date(),
                        'partner_id': self.partner_pizza_inn.id,
                    })
                    line2 = self.env['prescription.order'].create({
                        'product_id': self.product_sandwich_tuna.id,
                        'date': self.monday_1pm.date(),
                        'partner_id': self.partner_coin_gourmand.id,
                    })

                    (line | line2).action_order()
                    assert line.state == 'ordered'
                    assert line2.state == 'ordered'

                    self.partner_pizza_inn._send_auto_email()

                    assert line.state == 'confirmed'
                    assert line2.state == 'ordered'

                    line_1 = self.env['prescription.order'].create({
                        'product_id': self.product_pizza.id,
                        'quantity': 2,
                        'date': self.monday_1pm.date(),
                        'partner_id': self.product_pizza.id,
                    })

                    line_2 = self.env['prescription.order'].create({
                        'product_id': self.product_pizza.id,
                        'option_ids_1': [(6, 0, [self.option_olives.id])],
                        'date': self.monday_1pm.date(),
                        'partner_id': self.product_pizza.id,
                    })

                    line_3 = self.env['prescription.order'].create({
                        'product_id': self.product_sandwich_tuna.id,
                        'quantity': 2,
                        'date': self.monday_1pm.date(),
                        'partner_id': self.partner_coin_gourmand.id,
                    })

                    (line_1 | line_2 | line_3).action_order()

                    assert all(line.state == 'ordered' for line in [line_1, line_2, line_3])

                    self.partner_pizza_inn._send_auto_email()

    @common.users('cle-prescription-manager')
    def test_cron_sync_create(self):
        cron_ny = self.partner_kothai.cron_id  # I am at New-York
        self.assertTrue(cron_ny.active)
        self.assertEqual(cron_ny.name, "Prescription: send automatic email to Kothai")
        self.assertEqual(
            [line for line in cron_ny.code.splitlines() if not line.lstrip().startswith("#")],
            ["env['prescription.partner'].browse([%i])._send_auto_email()" % self.partner_kothai.id])
        self.assertEqual(cron_ny.nextcall, datetime(2021, 1, 29, 15, 0))  # New-york is UTC-5

    @common.users('cle-prescription-manager')
    def test_cron_sync_active(self):
        cron_ny = self.partner_kothai.cron_id

        self.partner_kothai.active = False
        self.assertFalse(cron_ny.active)
        self.partner_kothai.active = True
        self.assertTrue(cron_ny.active)

        self.partner_kothai.send_by = 'phone'
        self.assertFalse(cron_ny.active)
        self.partner_kothai.send_by = 'mail'
        self.assertTrue(cron_ny.active)

    @common.users('cle-prescription-manager')
    def test_cron_sync_nextcall(self):
        cron_ny = self.partner_kothai.cron_id
        old_nextcall = cron_ny.nextcall

        self.partner_kothai.automatic_email_time -= 5
        self.assertEqual(cron_ny.nextcall, old_nextcall - timedelta(hours=5) + timedelta(days=1))

        # Simulate cron execution
        cron_ny.sudo().lastcall = old_nextcall - timedelta(hours=5)
        cron_ny.sudo().nextcall += timedelta(days=1)

        self.partner_kothai.automatic_email_time += 7
        self.assertEqual(cron_ny.nextcall, old_nextcall + timedelta(days=1, hours=2))

        self.partner_kothai.automatic_email_time -= 1
        self.assertEqual(cron_ny.nextcall, old_nextcall + timedelta(days=1, hours=1))