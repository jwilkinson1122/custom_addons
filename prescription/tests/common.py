

from datetime import datetime
from freezegun import freeze_time
from odoo.tests import common, new_test_user


fakenow = datetime(2021, 1, 29, 12, 20, 0)

@freeze_time(fakenow)
class TestsCommon(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fakenow = fakenow

    def setUp(self):
        super(TestsCommon, self).setUp()

        self.env['prescription.cashmove'].create({
            'amount': 100,
        })

        self.manager = new_test_user(self.env, 'cle-prescription-manager', 'base.group_user,base.group_partner_manager,prescription.group_prescription_manager')
        with self.with_user('cle-prescription-manager'):

            self.location_office_1 = self.env['prescription.location'].create({
                'name' : 'Farm 1',
            })

            self.location_office_2 = self.env['prescription.location'].create({
                'name': 'Farm 2',
            })

            self.partner_pizza_inn = self.env['res.partner'].create({
                'name': 'Pizza Inn',
            })

            self.partner_pizza_inn = self.env['prescription.partner'].create({
                'partner_id': self.partner_pizza_inn.id,
                'send_by': 'mail',
                'automatic_email_time': 11,
                'available_location_ids': [
                    (6, 0, [self.location_office_1.id, self.location_office_2.id])
                ],
            })

            self.partner_kothai = self.env['res.partner'].create({
                'name': 'Kothai',
            })

            self.partner_kothai = self.env['prescription.partner'].create({
                'partner_id': self.partner_kothai.id,
                'send_by': 'mail',
                'automatic_email_time': 10,
                'tz': 'America/New_York',
            })

            self.partner_coin_gourmand = self.env['res.partner'].create({
                'name': 'Coin Gourmand',
            })

            self.partner_coin_gourmand = self.env['prescription.partner'].create({
                'partner_id': self.partner_coin_gourmand.id,
                'send_by': 'phone',
                'available_location_ids': [
                    (6, 0, [self.location_office_1.id, self.location_office_2.id])
                ],
            })

            self.category_pizza = self.env['prescription.product.category'].create({
                'name': 'Pizza',
            })

            self.category_sandwich = self.env['prescription.product.category'].create({
                'name': 'Sandwich',
            })

            self.product_pizza = self.env['prescription.product'].create({
                'name': 'Pizza',
                'category_id': self.category_pizza.id,
                'price': 9,
                'partner_id': self.partner_pizza_inn.id,
            })

            self.product_sandwich_tuna = self.env['prescription.product'].create({
                'name': 'Tuna Sandwich',
                'category_id': self.category_sandwich.id,
                'price': 3,
                'partner_id': self.partner_coin_gourmand.id,
            })

            self.option_olives = self.env['prescription.option'].create({
                'name': 'Olives',
                'price': 0.3,
                'partner_id': self.partner_pizza_inn.id,
            })

            self.env['prescription.cashmove'].create({
                'amount': 100,
            })

            self.alert_ny = self.env['prescription.alert'].create({
                'name': 'New York UTC-5',
                'mode': 'chat',
                'notification_time': 10,
                'notification_moment': 'am',
                'tz': 'America/New_York',
                'message': "",
            }).with_context(tz='America/New_York')

            self.alert_tokyo = self.env['prescription.alert'].create({
                'name': 'Tokyo UTC+9',
                'mode': 'chat',
                'notification_time': 8,
                'notification_moment': 'am',
                'tz': 'Asia/Tokyo',
                'message': "",
            }).with_context(tz='Asia/Tokyo')
