# -*- coding: utf-8 -*-

import base64

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase


class testAttachmentAccess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': "foo",
            'login': "foo",
            'email': "foo@bar.com",
            'groups_id': [(6, 0, [cls.env.ref('prescriptions.group_prescriptions_user').id])]
        })
        cls.prescription_defaults = {
            'folder_id': cls.env['prescriptions.folder'].create({'name': 'foo'}).id,
        }

    def test_user_prescription_attachment_without_res_fields(self):
        """Test an employee can create a prescription linked to an attachment without res_model/res_id"""
        env_user = self.env(user=self.user)
        # As user, create an attachment without res_model/res_id
        attachment = env_user['ir.attachment'].create({'name': 'foo', 'datas': base64.b64encode(b'foo')})
        # As user, create a prescription linked to that attachment
        prescription = env_user['prescriptions.prescription'].create({'attachment_id': attachment.id, **self.prescription_defaults})
        # As user, ensure the content of the attachment can be read through the prescription
        self.assertEqual(base64.b64decode(prescription.datas), b'foo')
        # As user, create another attachment without res_model/res_id
        attachment_2 = env_user['ir.attachment'].create({'name': 'foo', 'datas': base64.b64encode(b'bar')})
        # As user, change the attachment of the prescription to this second attachment
        prescription.write({'attachment_id': attachment_2.id})
        # As user, ensure the content of this second attachment can be read through the prescription
        self.assertEqual(base64.b64decode(prescription.datas), b'bar')

    def test_user_prescription_attachment_without_res_fields_created_by_admin(self):
        """Test an employee can read the content of the prescription's attachment created by another user, the admin,
        while the attachment does not have a res_model/res_id
        In prescriptions, there is a special mechanism setting the attachment res_model/res_id on creation of the prescription
        if the attachment res_model/res_id is not set. However, the same mechanism is not there in `write`.
        So, both cases need to be tested.
        """
        # As admin, create an attachment without res_model/res_id
        attachment = self.env['ir.attachment'].create({'name': 'foo', 'datas': base64.b64encode(b'foo')})
        # As admin, create a prescription linked to that attachment
        prescription = self.env['prescriptions.prescription'].create({'attachment_id': attachment.id, **self.prescription_defaults})
        # Ensure the attachment res_model/res_id have been set automatically
        self.assertEqual(attachment.res_model, 'prescriptions.prescription')
        self.assertEqual(attachment.res_id, prescription.id)

        # As user, ensure the attachment datas can be read directly and through the prescription
        self.env.invalidate_all()
        self.assertEqual(base64.b64decode(attachment.with_user(self.user).datas), b'foo')
        # As user, ensure the content of the attachment can be read through the prescription
        self.assertEqual(base64.b64decode(prescription.with_user(self.user).datas), b'foo')

        # As admin, create a second attachment without res_model/res_id
        attachment = self.env['ir.attachment'].create({'name': 'bar', 'datas': base64.b64encode(b'bar')})
        # As admin, link this second attachment to the previously created prescription (write instead of create)
        prescription.write({'attachment_id': attachment.id})
        # Ensure the res_model/res_id has not been set automatically during the write on the prescription
        self.assertFalse(attachment.res_model)
        self.assertFalse(attachment.res_id)

        # As user ensure the attachment itself cannot be read
        self.env.invalidate_all()
        with self.assertRaises(AccessError):
            self.assertEqual(base64.b64decode(attachment.with_user(self.user).datas), b'bar')
        # But, as user, the content of the attachment can be read through the prescription
        self.assertEqual(base64.b64decode(prescription.with_user(self.user).datas), b'bar')

    def test_user_read_unallowed_attachment(self):
        """Test a user cannot access an attachment he is not supposed to through a prescription"""
        # As admin, create an attachment for which you require the settings group to access
        autovacuum_job = self.env.ref('base.autovacuum_job')
        attachment_forbidden = self.env['ir.attachment'].create({
            'name': 'foo', 'datas': base64.b64encode(b'foo'),
            'res_model': autovacuum_job._name, 'res_id': autovacuum_job.id,
        })
        # As user, make sure this is indeed not possible to access that attachment data directly
        self.env.invalidate_all()
        with self.assertRaises(AccessError):
            attachment_forbidden.with_user(self.user).datas
        # As user, create a prescription pointing to that attachment
        # and make sure it raises an access error
        with self.assertRaises(AccessError):
            prescription = self.env['prescriptions.prescription'].with_user(self.user).create({
                'attachment_id': attachment_forbidden.id,
                **self.prescription_defaults,
            })
            prescription.datas

        # As user, update the attachment of an existing prescription to the unallowed attachment
        # and make sure it raises an access error
        attachment_tmp = self.env['ir.attachment'].with_user(self.user).create({
            'name': 'bar', 'datas': base64.b64encode(b'bar'),
        })
        prescription = self.env['prescriptions.prescription'].with_user(self.user).create({
            'attachment_id': attachment_tmp.id,
            **self.prescription_defaults,
        })
        with self.assertRaises(AccessError):
            prescription.write({'attachment_id': attachment_forbidden.id})
            prescription.datas
