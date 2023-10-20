# -*- coding: utf-8 -*-

from odoo.tests import Form
from odoo.addons.pod_manager.tests.common import TestPodCommon


class TestPodPractitioner(TestPodCommon):

    def setUp(self):
        super().setUp()
        self.user_without_image = self.env['res.users'].create({
            'name': 'Marc Demo',
            'email': 'mark.brown23@example.com',
            'image_1920': False,
            'login': 'demo_1',
            'password': 'demo_123'
        })
        self.practitioner_without_image = self.env['pod.practitioner'].create({
            'user_id': self.user_without_image.id,
            'image_1920': False
        })

    def test_practitioner_resource(self):
        _tz = 'Pacific/Apia'
        self.res_users_pod_officer.company_id.resource_calendar_id.tz = _tz
        Practitioner = self.env['pod.practitioner'].with_user(self.res_users_pod_officer)
        practitioner_form = Form(Practitioner)
        practitioner_form.name = 'Raoul Grosbedon'
        practitioner_form.practice_email = 'raoul@example.com'
        practitioner = practitioner_form.save()
        self.assertEqual(practitioner.tz, _tz)

    def test_practitioner_from_user(self):
        _tz = 'Pacific/Apia'
        _tz2 = 'America/Tijuana'
        self.res_users_pod_officer.company_id.resource_calendar_id.tz = _tz
        self.res_users_pod_officer.tz = _tz2
        Practitioner = self.env['pod.practitioner'].with_user(self.res_users_pod_officer)
        practitioner_form = Form(Practitioner)
        practitioner_form.name = 'Raoul Grosbedon'
        practitioner_form.practice_email = 'raoul@example.com'
        practitioner_form.user_id = self.res_users_pod_officer
        practitioner = practitioner_form.save()
        self.assertEqual(practitioner.name, 'Raoul Grosbedon')
        self.assertEqual(practitioner.practice_email, self.res_users_pod_officer.email)
        self.assertEqual(practitioner.tz, self.res_users_pod_officer.tz)

    def test_practitioner_from_user_tz_no_reset(self):
        _tz = 'Pacific/Apia'
        self.res_users_pod_officer.tz = False
        Practitioner = self.env['pod.practitioner'].with_user(self.res_users_pod_officer)
        practitioner_form = Form(Practitioner)
        practitioner_form.name = 'Raoul Grosbedon'
        practitioner_form.practice_email = 'raoul@example.com'
        practitioner_form.tz = _tz
        practitioner_form.user_id = self.res_users_pod_officer
        practitioner = practitioner_form.save()
        self.assertEqual(practitioner.name, 'Raoul Grosbedon')
        self.assertEqual(practitioner.practice_email, self.res_users_pod_officer.email)
        self.assertEqual(practitioner.tz, _tz)

    def test_practitioner_has_avatar_even_if_it_has_no_image(self):
        self.assertTrue(self.practitioner_without_image.avatar_128)
        self.assertTrue(self.practitioner_without_image.avatar_256)
        self.assertTrue(self.practitioner_without_image.avatar_512)
        self.assertTrue(self.practitioner_without_image.avatar_1024)
        self.assertTrue(self.practitioner_without_image.avatar_1920)

    def test_practitioner_has_same_avatar_as_corresponding_user(self):
        self.assertEqual(self.practitioner_without_image.avatar_1920, self.user_without_image.avatar_1920)
