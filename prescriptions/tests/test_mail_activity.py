# -*- coding: utf-8 -*-


from odoo.tests.common import TransactionCase
import base64

GIF = b"R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs="
TEXT = base64.b64encode(bytes("TEST", 'utf-8'))


class TestCasePrescriptions(TransactionCase):

    def setUp(self):
        super(TestCasePrescriptions, self).setUp()
        self.doc_user = self.env['res.users'].create({
            'name': 'Test user prescriptions',
            'login': 'prescriptions@example.com',
        })
        self.doc_partner = self.env['res.partner'].create({
             'name': 'Luke Skywalker',
        })
        self.folder_a = self.env['prescriptions.folder'].create({
            'name': 'folder A',
        })
        self.folder_a_a = self.env['prescriptions.folder'].create({
            'name': 'folder A - A',
            'parent_folder_id': self.folder_a.id,
        })
        self.folder_b = self.env['prescriptions.folder'].create({
            'name': 'folder B',
        })
        self.tag_category_b = self.env['prescriptions.facet'].create({
            'folder_id': self.folder_b.id,
            'name': "categ_b",
        })
        self.tag_b = self.env['prescriptions.tag'].create({
            'facet_id': self.tag_category_b.id,
            'name': "tag_b",
        })
        self.tag_category_a = self.env['prescriptions.facet'].create({
            'folder_id': self.folder_a.id,
            'name': "categ_a",
        })
        self.tag_category_a_a = self.env['prescriptions.facet'].create({
            'folder_id': self.folder_a_a.id,
            'name': "categ_a_a",
        })
        self.tag_a_a = self.env['prescriptions.tag'].create({
            'facet_id': self.tag_category_a_a.id,
            'name': "tag_a_a",
        })
        self.tag_a = self.env['prescriptions.tag'].create({
            'facet_id': self.tag_category_a.id,
            'name': "tag_a",
        })

    def test_request_activity(self):
        """
        Makes sure the prescription request activities are working properly
        """
        partner = self.env['res.partner'].create({'name': 'Pepper Street'})
        activity_type = self.env['mail.activity.type'].create({
            'name': 'test_activity_type',
            'category': 'upload_file',
            'folder_id': self.folder_a.id,
        })
        activity = self.env['mail.activity'].create({
            'activity_type_id': activity_type.id,
            'user_id': self.doc_user.id,
            'res_id': partner.id,
            'res_model_id': self.env['ir.model'].search([('model', '=', 'res.partner')], limit=1).id,
            'summary': 'test_summary',
        })

        activity_2 = self.env['mail.activity'].create({
            'activity_type_id': activity_type.id,
            'user_id': self.doc_user.id,
            'res_id': partner.id,
            'res_model_id': self.env['ir.model'].search([('model', '=', 'res.partner')], limit=1).id,
            'summary': 'test_summary_2',
        })

        attachment = self.env['ir.attachment'].create({
            'datas': GIF,
            'name': 'Test activity 1',
        })

        prescription_1 = self.env['prescriptions.prescription'].search([('request_activity_id', '=', activity.id)], limit=1)
        prescription_2 = self.env['prescriptions.prescription'].search([('request_activity_id', '=', activity_2.id)], limit=1)

        self.assertEqual(prescription_1.name, 'test_summary', 'the activity prescription should have the right name')
        self.assertEqual(prescription_1.folder_id.id, self.folder_a.id, 'the prescription 1 should have the right folder')
        self.assertEqual(prescription_2.folder_id.id, self.folder_a.id, 'the prescription 2 should have the right folder')
        activity._action_done(attachment_ids=[attachment.id])
        prescription_2.write({'datas': TEXT, 'name': 'new filename'})
        self.assertEqual(prescription_1.attachment_id.id, attachment.id,
                         'the prescription should have the newly added attachment')
        self.assertFalse(activity.exists(), 'the activity should be done')
        self.assertFalse(activity_2.exists(), 'the activity_2 should be done')

    def test_recurring_prescription_request(self):
        """
        Ensure that separate prescription requests are created for recurring upload activities
        Ensure that the next activity is linked to the new prescription
        """
        activity_type = self.env['mail.activity.type'].create({
            'name': 'recurring_upload_activity_type',
            'category': 'upload_file',
            'folder_id': self.folder_a.id,
        })
        activity_type.write({
            'chaining_type': 'trigger',
            'triggered_next_type_id': activity_type.id
        })
        prescription = self.env['prescriptions.request_wizard'].create({
            'name': 'Wizard Request',
            'requestee_id': self.doc_partner.id,
            'activity_type_id': activity_type.id,
            'folder_id': self.folder_a.id,
        }).request_prescription()
        activity = prescription.request_activity_id

        self.assertEqual(activity.summary, 'Wizard Request')

        prescription.write({'datas': GIF, 'name': 'testGif.gif'})

        self.assertFalse(activity.exists(), 'the activity should be removed after file upload')
        self.assertEqual(prescription.type, 'binary', 'prescription 1 type should be binary')
        self.assertFalse(prescription.request_activity_id, 'prescription 1 should have no activity remaining')

        # a new prescription (request) and file_upload activity should be created
        activity_2 = self.env['mail.activity'].search([('res_model', '=', 'prescriptions.prescription')])
        prescription_2 = self.env['prescriptions.prescription'].search([('request_activity_id', '=', activity_2.id), ('type', '=', 'empty')])

        self.assertNotEqual(prescription_2.id, prescription.id, 'a new prescription and activity should exist')
        self.assertEqual(prescription_2.request_activity_id.summary, 'Wizard Request')
