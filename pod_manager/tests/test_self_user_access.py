# -*- coding: utf-8 -*-

from collections import OrderedDict
from itertools import chain

from odoo.addons.pod_manager.tests.common import TestPodCommon
from odoo.tests import new_test_user, tagged, Form
from odoo.exceptions import AccessError

@tagged('post_install', '-at_install')
class TestSelfAccessProfile(TestPodCommon):

    def test_access_user_profile(self):
        """ A simple user should be able to read all fields in his profile """
        james = new_test_user(self.env, login='hel', groups='base.group_user', name='Simple practitioner', email='ric@example.com')
        james = james.with_user(james)
        self.env['pod.practitioner'].create({
            'name': 'James',
            'user_id': james.id,
        })
        view = self.env.ref('pod_manager.res_users_view_form_profile')
        view_infos = james.fields_view_get(view_id=view.id)
        fields = view_infos['fields'].keys()
        james.read(fields)

    def test_readonly_fields(self):
        """ Practitioner related fields should be readonly if self editing is not allowed """
        self.env['ir.config_parameter'].sudo().set_param('pod_manager.pod_practitioner_self_edit', False)
        james = new_test_user(self.env, login='hel', groups='base.group_user', name='Simple practitioner', email='ric@example.com')
        james = james.with_user(james)
        self.env['pod.practitioner'].create({
            'name': 'James',
            'user_id': james.id,
        })

        view = self.env.ref('pod_manager.res_users_view_form_profile')
        view_infos = james.fields_view_get(view_id=view.id)

        practitioner_related_fields = {
            field_name
            for field_name, field_attrs in view_infos['fields'].items()
            if field_attrs.get('related', (None,))[0] == 'practitioner_id'
        }

        form = Form(james, view=view)
        for field in practitioner_related_fields:
            with self.assertRaises(AssertionError, msg="Field '%s' should be readonly in the practitioner profile when self editing is not allowed." % field):
                form.__setattr__(field, 'some value')


    def test_profile_view_fields(self):
        """ A simple user should see all fields in profile view, even if they are protected by groups """
        view = self.env.ref('pod_manager.res_users_view_form_profile')

        # For reference, check the view with user with every groups protecting user fields
        all_groups_xml_ids = chain(*[
            field.groups.split(',')
            for field in self.env['res.users']._fields.values()
            if field.groups
            if field.groups != '.' # "no-access" group on purpose
        ])
        all_groups = self.env['res.groups']
        for xml_id in all_groups_xml_ids:
            all_groups |= self.env.ref(xml_id.strip())
        user_all_groups = new_test_user(self.env, groups='base.group_user', login='hel', name='God')
        user_all_groups.write({'groups_id': [(4, group.id, False) for group in all_groups]})
        view_infos = self.env['res.users'].with_user(user_all_groups).fields_view_get(view_id=view.id)
        full_fields = view_infos['fields']

        # Now check the view for a simple user
        user = new_test_user(self.env, login='gro', name='Grouillot')
        view_infos = self.env['res.users'].with_user(user).fields_view_get(view_id=view.id)
        fields = view_infos['fields']

        # Compare both
        self.assertEqual(full_fields.keys(), fields.keys(), "View fields should not depend on user's groups")

    def test_access_user_profile_toolbar(self):
        """ A simple user shouldn't have the possibilities to see the 'Change Password' action"""
        james = new_test_user(self.env, login='jam', groups='base.group_user', name='Simple practitioner', email='jam@example.com')
        james = james.with_user(james)
        self.env['pod.practitioner'].create({
            'name': 'James',
            'user_id': james.id,
        })
        view = self.env.ref('pod_manager.res_users_view_form_profile')
        available_actions = james.fields_view_get(view_id=view.id, toolbar=True)['toolbar']['action']
        change_password_action = self.env.ref("base.change_password_wizard_action")

        self.assertFalse(any(x['id'] == change_password_action.id for x in available_actions))

        """ An ERP manager should have the possibilities to see the 'Change Password' """
        john = new_test_user(self.env, login='joh', groups='base.group_erp_manager', name='ERP Manager', email='joh@example.com')
        john = john.with_user(john)
        self.env['pod.practitioner'].create({
            'name': 'John',
            'user_id': john.id,
        })
        view = self.env.ref('pod_manager.res_users_view_form_profile')
        available_actions = john.fields_view_get(view_id=view.id, toolbar=True)['toolbar']['action']
        self.assertTrue(any(x['id'] == change_password_action.id for x in available_actions))


class TestSelfAccessRights(TestPodCommon):

    def setUp(self):
        super(TestSelfAccessRights, self).setUp()
        self.richard = new_test_user(self.env, login='ric', groups='base.group_user', name='Simple practitioner', email='ric@example.com')
        self.richard_emp = self.env['pod.practitioner'].create({
            'name': 'Richard',
            'user_id': self.richard.id,
            'private_address_id': self.env['res.partner'].create({'name': 'Richard', 'phone': '21454', 'type': 'private'}).id,
        })
        self.hubert = new_test_user(self.env, login='hub', groups='base.group_user', name='Simple practitioner', email='hub@example.com')
        self.hubert_emp = self.env['pod.practitioner'].create({
            'name': 'Hubert',
            'user_id': self.hubert.id,
            'private_address_id': self.env['res.partner'].create({'name': 'Hubert', 'type': 'private'}).id,
        })

        self.protected_fields_emp = OrderedDict([(k, v) for k, v in self.env['pod.practitioner']._fields.items() if v.groups == 'pod_manager.group_pod_user'])
        # Compute fields and id field are always readable by everyone
        self.read_protected_fields_emp = OrderedDict([(k, v) for k, v in self.env['pod.practitioner']._fields.items() if not v.compute and k != 'id'])
        self.self_protected_fields_user = OrderedDict([
            (k, v)
            for k, v in self.env['res.users']._fields.items()
            if v.groups == 'pod_manager.group_pod_user' and k in self.env['res.users'].SELF_READABLE_FIELDS
        ])

    # Read pod.practitioner #
    def testReadSelfPractitioner(self):
        with self.assertRaises(AccessError):
            self.hubert_emp.with_user(self.richard).read(self.protected_fields_emp.keys())

    def testReadOtherPractitioner(self):
        with self.assertRaises(AccessError):
            self.hubert_emp.with_user(self.richard).read(self.protected_fields_emp.keys())

    # Write pod.practitioner #
    def testWriteSelfPractitioner(self):
        for f in self.protected_fields_emp:
            with self.assertRaises(AccessError):
                self.richard_emp.with_user(self.richard).write({f: 'dummy'})

    def testWriteOtherPractitioner(self):
        for f in self.protected_fields_emp:
            with self.assertRaises(AccessError):
                self.hubert_emp.with_user(self.richard).write({f: 'dummy'})

    # Read res.users #
    def testReadSelfUserPractitioner(self):
        for f in self.self_protected_fields_user:
            self.richard.with_user(self.richard).read([f])  # should not raise

    def testReadOtherUserPractitioner(self):
        with self.assertRaises(AccessError):
            self.hubert.with_user(self.richard).read(self.self_protected_fields_user)

    # Write res.users #
    def testWriteSelfUserPractitionerSettingFalse(self):
        for f, v in self.self_protected_fields_user.items():
            with self.assertRaises(AccessError):
                self.richard.with_user(self.richard).write({f: 'dummy'})

    def testWriteSelfUserPractitioner(self):
        self.env['ir.config_parameter'].set_param('pod_manager.pod_practitioner_self_edit', True)
        for f, v in self.self_protected_fields_user.items():
            val = None
            if v.type == 'char' or v.type == 'text':
                val = '0000' if f == 'pin' else 'dummy'
            if val is not None:
                self.richard.with_user(self.richard).write({f: val})

    def testWriteSelfUserPreferencesPractitioner(self):
        # self should always be able to update non pod.practitioner fields if
        # they are in SELF_READABLE_FIELDS
        self.env['ir.config_parameter'].set_param('pod_manager.pod_practitioner_self_edit', False)
        # should not raise
        vals = [
            {'tz': "Australia/ACT"},
            {'email': "new@example.com"},
            {'signature': "<p>I'm Richard!</p>"},
            {'notification_type': "email"},
        ]
        for v in vals:
            # should not raise
            self.richard.with_user(self.richard).write(v)

    def testWriteOtherUserPreferencesPractitioner(self):
        # self should always be able to update non pod.practitioner fields if
        # they are in SELF_READABLE_FIELDS
        self.env['ir.config_parameter'].set_param('pod_manager.pod_practitioner_self_edit', False)
        vals = [
            {'tz': "Australia/ACT"},
            {'email': "new@example.com"},
            {'signature': "<p>I'm Richard!</p>"},
            {'notification_type': "email"},
        ]
        for v in vals:
            with self.assertRaises(AccessError):
                self.hubert.with_user(self.richard).write(v)

    def testWriteSelfPhonePractitioner(self):
        # phone is a related from res.partner (from base) but added in SELF_READABLE_FIELDS
        self.env['ir.config_parameter'].set_param('pod_manager.pod_practitioner_self_edit', False)
        with self.assertRaises(AccessError):
            self.richard.with_user(self.richard).write({'phone': '2154545'})

    def testWriteOtherUserPractitioner(self):
        for f in self.self_protected_fields_user:
            with self.assertRaises(AccessError):
                self.hubert.with_user(self.richard).write({f: 'dummy'})

    def testSearchUserEMployee(self):
        # Searching user based on practitioner_id field should not raise bad query error
        self.env['res.users'].with_user(self.richard).search([('practitioner_id', 'ilike', 'Hubert')])
