# -*- coding: utf-8 -*-

import base64

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import mute_logger

from psycopg2 import IntegrityError


class TestCaseSecurity(TransactionCase):

    def setUp(self):
        super(TestCaseSecurity, self).setUp()
        self.arbitrary_group = self.env['res.groups'].create({
            'name': 'arbitrary_group',
            'implied_ids': [(6, 0, [self.ref('base.group_user')])],
        })

        self.basic_user = self.env['res.users'].create({
            'name': "prescriptions test basic user",
            'login': "dtbu",
            'email': "dtbu@yourcompany.com",
            'groups_id': [(6, 0, [self.ref('base.group_user')])]
        })
        self.prescription_user = self.env['res.users'].create({
            'name': "prescriptions test prescriptions user",
            'login': "dtdu",
            'email': "dtdu@yourcompany.com",
            'groups_id': [(6, 0, [self.ref('prescriptions.group_prescriptions_user')])]
        })
        self.test_group_user = self.env['res.users'].create({
            'name': "prescriptions test group user",
            'login': "dtgu",
            'email': "dtgu@yourcompany.com",
            'groups_id': [(6, 0, [self.arbitrary_group.id])]
        })
        self.test_group_user2 = self.env['res.users'].create({
            'name': "prescriptions test group user2",
            'login': "dtgu2",
            'email': "dtgu2@yourcompany.com",
            'groups_id': [(6, 0, [self.arbitrary_group.id])]
        })
        self.prescription_manager = self.env['res.users'].create({
            'name': "prescriptions test prescriptions manager",
            'login': "dtdm",
            'email': "dtdm@yourcompany.com",
            'groups_id': [(6, 0, [self.ref('prescriptions.group_prescriptions_manager')])]
        })

    def test_prescriptions_access_default(self):
        """
        Tests the access rights for a prescription where no access_group is specified
        users should default in read/write.
        """

        folder_d = self.env['prescriptions.folder'].create({
            'name': 'folder D',
        })
        prescription_d = self.env['prescriptions.prescription'].create({
            'name': 'prescription D',
            'folder_id': folder_d.id,
        })

        expected_read_result = [{'id': prescription_d.id, 'name': 'prescription D'}]

        basic_user_doc_d_read_result = prescription_d.with_user(self.basic_user).read(['name'])
        self.assertEqual(basic_user_doc_d_read_result, expected_read_result,
                         'test_group_user should be able to read prescription_d')
        doc_d_read_result = prescription_d.with_user(self.prescription_user).read(['name'])
        self.assertEqual(doc_d_read_result, expected_read_result,
                         'prescription_user should be able to read prescription_d')

        prescription_d.with_user(self.basic_user).write({'name': 'basic_user_write'})
        self.assertEqual(prescription_d.name, 'basic_user_write')
        prescription_d.with_user(self.prescription_user).write({'name': 'prescription_user_write'})
        self.assertEqual(prescription_d.name, 'prescription_user_write')
        prescription_d.with_user(self.test_group_user).write({'name': 'user_write'})
        self.assertEqual(prescription_d.name, 'user_write')
        prescription_d.with_user(self.prescription_manager).write({'name': 'prescription_manager_write'})
        self.assertEqual(prescription_d.name, 'prescription_manager_write')

    def test_prescriptions_access_manager_read_write(self):
        """
        Tests the access rights for a prescription where group_prescriptions_manager is the only group with access (read/write).
        """

        folder_a = self.env['prescriptions.folder'].create({
            'name': 'folder A',
            'group_ids': [(6, 0, [self.ref('prescriptions.group_prescriptions_manager')])],
        })

        prescription_a = self.env['prescriptions.prescription'].create({
            'name': 'prescription A',
            'folder_id': folder_a.id,
        })

        with self.assertRaises(AccessError):
            prescription_a.with_user(self.basic_user).read()
        with self.assertRaises(AccessError):
            prescription_a.with_user(self.test_group_user).read()
        with self.assertRaises(AccessError):
            prescription_a.with_user(self.prescription_user).read()
        with self.assertRaises(AccessError):
            prescription_a.with_user(self.basic_user).write({'name': 'nameChangedA'})
        with self.assertRaises(AccessError):
            prescription_a.with_user(self.test_group_user).write({'name': 'nameChangedA'})
        with self.assertRaises(AccessError):
            prescription_a.with_user(self.prescription_user).write({'name': 'nameChangedA'})

        prescription_a.with_user(self.prescription_manager).write({'name': 'nameChangedManagerA'})
        self.assertEqual(prescription_a.name, 'nameChangedManagerA',
                         'prescription manager should be able to write prescription_a')

    def test_prescriptions_access_arbitrary_readonly(self):
        """
        Tests the access rights for a prescription where arbitrary_group is the only group with access (read).
        """
        
        folder_b = self.env['prescriptions.folder'].create({
            'name': 'folder B',
            'read_group_ids': [(6, 0, [self.arbitrary_group.id])],
        })
        prescription_b = self.env['prescriptions.prescription'].create({
            'name': 'prescription B',
            'folder_id': folder_b.id,
        })

        with self.assertRaises(AccessError):
            prescription_b.with_user(self.basic_user).read()
        with self.assertRaises(AccessError):
            prescription_b.with_user(self.prescription_user).read()
        with self.assertRaises(AccessError):
            prescription_b.with_user(self.basic_user).write({'name': 'nameChangedB'})
        with self.assertRaises(AccessError):
            prescription_b.with_user(self.prescription_user).write({'name': 'nameChangedB'})
        with self.assertRaises(AccessError):
            prescription_b.with_user(self.test_group_user).write({'name': 'nameChangedB'})

        prescription_b.with_user(self.test_group_user).toggle_favorited()
        self.assertFalse(prescription_b.is_favorited)

        test_group_user_prescription_b_name = prescription_b.with_user(self.test_group_user).read(['name'])
        self.assertEqual(test_group_user_prescription_b_name, [{'id': prescription_b.id, 'name': 'prescription B'}],
                         'test_group_user should be able to read prescription_b')

    def test_prescriptions_arbitrary_read_write(self):
        """
        Tests the access rights for a prescription where arbitrary_group is the only group with access (read/write).
        The group_prescriptions_manager always keeps the read/write access.
        """

        folder_c = self.env['prescriptions.folder'].create({
            'name': 'folder C',
            'group_ids': [(6, 0, [self.arbitrary_group.id])],
        })
        prescription_c = self.env['prescriptions.prescription'].create({
            'name': 'prescription C',
            'folder_id': folder_c.id,
        })

        with self.assertRaises(AccessError):
            prescription_c.with_user(self.basic_user).read()
        with self.assertRaises(AccessError):
            prescription_c.with_user(self.prescription_user).read()
        with self.assertRaises(AccessError):
            prescription_c.with_user(self.basic_user).write({'name': 'nameChangedC'})
        with self.assertRaises(AccessError):
            prescription_c.with_user(self.prescription_user).write({'name': 'nameChangedC'})

        prescription_c.with_user(self.test_group_user).write({'name': 'nameChanged'})
        self.assertEqual(prescription_c.name, 'nameChanged',
                         'test_group_user should be able to write prescription_c')
        prescription_c.with_user(self.prescription_manager).write({'name': 'nameChangedManager'})
        self.assertEqual(prescription_c.name, 'nameChangedManager',
                         'prescription manager should be able to write prescription_c')

    def test_prescriptions_access(self):
        """
        Tests the access rights for a prescription where 'user_specific' is True.
        Users should be limited to records for which they are the owner only if they are limited to read.
        """

        arbitrary_group2 = self.env['res.groups'].create({
            'name': 'arbitrary_group2',
            'implied_ids': [(6, 0, [self.ref('base.group_user')])],
        })
        test_group2_user = self.env['res.users'].create({
            'name': "prescriptions test group user21",
            'login': "dtgu21",
            'email': "dtgu21@yourcompany.com",
            'groups_id': [(6, 0, [arbitrary_group2.id])]
        })
        folder_owner = self.env['prescriptions.folder'].create({
            'name': 'folder owner',
            'group_ids': [(6, 0, [self.arbitrary_group.id])],
            'read_group_ids': [(6, 0, [arbitrary_group2.id])],
            'user_specific': True,
        })
        prescription_owner = self.env['prescriptions.prescription'].create({
            'name': 'prescription owner',
            'folder_id': folder_owner.id,
            'owner_id': self.test_group_user.id,
        })
        prescription_owner2 = self.env['prescriptions.prescription'].create({
            'name': 'prescription owner2',
            'folder_id': folder_owner.id,
            'owner_id': self.test_group_user2.id,
        })
        prescription_not_owner = self.env['prescriptions.prescription'].create({
            'name': 'prescription not owner',
            'folder_id': folder_owner.id,
        })
        prescription_read_owner = self.env['prescriptions.prescription'].create({
            'name': 'prescription read owner',
            'folder_id': folder_owner.id,
            'owner_id': test_group2_user.id,
        })


        # prescriptions access by owner
        with self.assertRaises(AccessError):
            prescription_not_owner.with_user(self.basic_user).read()
        with self.assertRaises(AccessError):
            prescription_not_owner.with_user(test_group2_user).read()
        with self.assertRaises(AccessError):
            prescription_not_owner.with_user(self.prescription_user).read()
        with self.assertRaises(AccessError):
            prescription_not_owner.with_user(self.basic_user).write({'name': 'nameChangedA'})
        with self.assertRaises(AccessError):
            prescription_not_owner.with_user(self.prescription_user).write({'name': 'nameChangedA'})

        with self.assertRaises(AccessError):
            prescription_owner.with_user(self.basic_user).read()
        with self.assertRaises(AccessError):
            prescription_owner.with_user(self.prescription_user).read()
        with self.assertRaises(AccessError):
            prescription_owner.with_user(test_group2_user).read()
        with self.assertRaises(AccessError):
            prescription_owner.with_user(self.basic_user).write({'name': 'nameChangedA'})
        with self.assertRaises(AccessError):
            prescription_owner.with_user(self.prescription_user).write({'name': 'nameChangedA'})

        with self.assertRaises(AccessError):
            prescription_owner2.with_user(test_group2_user).read()

        name_from_read_owner = prescription_read_owner.with_user(test_group2_user).name
        self.assertEqual(name_from_read_owner, prescription_read_owner.name,
                         'test_group2_user should be able to read his own prescription')

        prescription_owner.with_user(self.test_group_user).write({'name': 'nameChangedOwner'})
        self.assertEqual(prescription_owner.name, 'nameChangedOwner',
                         'test_group_user should be able to write prescription_owner')
        prescription_from_user = self.env['prescriptions.prescription'].with_user(self.test_group_user).browse(
            prescription_not_owner.id)
        self.assertEqual(prescription_from_user.name, 'prescription not owner',
                         'test_group_user should be able to read prescription_not_owner as he is in the write group')
        prescription_not_owner.with_user(self.test_group_user).write({'name': 'nameChangedA'})
        self.assertEqual(prescription_not_owner.name, 'nameChangedA',
                         'test_group_user should be able to write prescription_not_owner as he is in the write group')

        # We now set the prescription to user_specific for write permissions.
        folder_owner.user_specific_write = True
        # since the user is not in the folder's write group, they will not be able to write the prescriptions
        with self.assertRaises(AccessError):
            prescription_read_owner.with_user(test_group2_user).write({'name': 'nameChange'})
        # the first user is in the write groups but is not the owner of the prescription
        with self.assertRaises(AccessError):
            prescription_read_owner.with_user(self.test_group_user).write({'name': 'nameChange'})

        # Now give the right group to test_group2_user.
        test_group2_user.groups_id += self.arbitrary_group
        # they should now be able to write on the prescription
        prescription_read_owner.with_user(test_group2_user).write({'name': 'nameChangedC'})

    def test_share_link_access(self):
        """
        Tests access rights for share links when the access rights of the folder is changed after the creation of the link.
        """

        folder_share = self.env['prescriptions.folder'].create({
            'name': 'folder share',
        })
        prescription = self.env['prescriptions.prescription'].create({
            'datas': b"R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=",
            'name': 'file.gif',
            'mimetype': 'image/gif',
            'folder_id': folder_share.id,
        })
        test_share = self.env['prescriptions.share'].with_user(self.prescription_user).create({
            'folder_id': folder_share.id,
            'type': 'ids',
            'prescription_ids': [(6, 0, [prescription.id])]
        })
        available_prescriptions = test_share._get_prescriptions_and_check_access(test_share.access_token, operation='read')
        self.assertEqual(len(available_prescriptions), 1,
                         'This method should indicate that the create_uid has access to the folder')
        folder_share.write({'group_ids': [(6, 0, [self.ref('prescriptions.group_prescriptions_manager')])]})
        available_prescriptions = test_share._get_prescriptions_and_check_access(test_share.access_token, operation='read')
        self.assertEqual(len(available_prescriptions), 0,
                         'This method should indicate that the create_uid doesnt have access to the folder anymore')

    def test_share_link_dynamic_access(self):
        """
        Test the dynamic change of prescriptions available from share links when access conditions change.
        """

        TEXT = base64.b64encode(bytes("TEST", 'utf-8'))
        folder_share = self.env['prescriptions.folder'].create({
            'name': 'folder share',
            'read_group_ids': [(6, 0, [self.ref('prescriptions.group_prescriptions_user')])]
        })
        prescription_a = self.env['prescriptions.prescription'].create({
            'datas': b"R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=",
            'owner_id': self.prescription_manager.id,
            'name': 'filea.gif',
            'mimetype': 'image/gif',
            'folder_id': folder_share.id,
        })
        prescription_b = self.env['prescriptions.prescription'].create({
            'datas': TEXT,
            'owner_id': self.prescription_manager.id,
            'name': 'fileb.gif',
            'mimetype': 'image/gif',
            'folder_id': folder_share.id,
        })
        prescription_c = self.env['prescriptions.prescription'].create({
            'datas': TEXT,
            'owner_id': self.prescription_user.id,
            'name': 'filec.gif',
            'mimetype': 'image/gif',
            'folder_id': folder_share.id,
        })
        test_share = self.env['prescriptions.share'].with_user(self.prescription_user).create({
            'folder_id': folder_share.id,
            'type': 'ids',
            'prescription_ids': [(6, 0, [prescription_a.id, prescription_b.id, prescription_c.id])]
        })
        available_prescriptions = test_share._get_prescriptions_and_check_access(test_share.access_token, operation='read')
        self.assertEqual(len(available_prescriptions), 3, "there should be 3 available prescriptions")

        folder_share.write({'user_specific': True})
        available_prescriptions = test_share._get_prescriptions_and_check_access(test_share.access_token, operation='read')
        self.assertEqual(len(available_prescriptions), 1, "there should be 1 available prescription")
        self.assertEqual(available_prescriptions.name, 'filec.gif', "the prescription C should be available")

    def test_share_parent_folder_with_ids(self):
        """
        Tests the access rights of a share link when the parent folder is shared with ids.
        """
        TEXT = base64.b64encode(bytes("TEST", 'utf-8'))
        folder_share_parent = self.env['prescriptions.folder'].create({
            'name': 'folder share',
            'read_group_ids': [(6, 0, [self.ref('prescriptions.group_prescriptions_user')])]
        })
        folder_share_child_a = self.env['prescriptions.folder'].create({
            'name': 'folder share',
            'parent_folder_id': folder_share_parent.id,
            'read_group_ids': [(6, 0, [self.ref('prescriptions.group_prescriptions_user')])]
        })
        folder_share_child_b = self.env['prescriptions.folder'].create({
            'name': 'folder share',
            'parent_folder_id': folder_share_parent.id,
            'read_group_ids': [(6, 0, [self.ref('prescriptions.group_prescriptions_user')])]
        })
        prescription_a = self.env['prescriptions.prescription'].create({
            'datas': b"R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=",
            'owner_id': self.prescription_manager.id,
            'name': 'filea.gif',
            'mimetype': 'image/gif',
            'folder_id': folder_share_child_a.id,
        })
        prescription_b = self.env['prescriptions.prescription'].create({
            'datas': TEXT,
            'owner_id': self.prescription_manager.id,
            'name': 'fileb.gif',
            'mimetype': 'image/gif',
            'folder_id': folder_share_child_b.id,
        })
        test_share = self.env['prescriptions.share'].with_user(self.prescription_user).create({
            'folder_id': folder_share_parent.id,
            'type': 'ids',
            'prescription_ids': [(6, 0, [prescription_a.id, prescription_b.id])]
        })

        available_prescriptions = test_share._get_prescriptions_and_check_access(test_share.access_token, operation='read')
        self.assertEqual(len(available_prescriptions), 2, "there should be 2 available prescriptions")

    def test_folder_user_specific_write(self):
        """
        Tests that `user_specific_write` is disabled when `user_specific` is disabled
        """
        folder = self.env['prescriptions.folder'].create({
            'name': 'Test Folder',
            'user_specific': True,
            'user_specific_write': True,
        })

        folder.user_specific = False
        self.assertFalse(folder.user_specific_write)

        with mute_logger('odoo.sql_db'):
            with self.assertRaises(IntegrityError):
                with self.cr.savepoint():
                    folder.write({'user_specific_write': True})

    def test_folder_has_write_access(self):
        """
        Tests that user has right write  access for folder using `has_write_access`.
        """

        # No groups on folder
        folder = self.env['prescriptions.folder'].create({
            'name': 'Test Folder',
        })

        self.assertTrue(folder.with_user(self.prescription_manager).has_write_access, "Prescription manager should have write access on folder")
        self.assertTrue(folder.with_user(self.prescription_user).has_write_access, "Prescription user should have write access on folder")

        # manager can write and arbitary group can read
        folder.write({
            'group_ids': [(6, 0, [self.ref('prescriptions.group_prescriptions_manager')])],
            'read_group_ids': [(6, 0, [self.arbitrary_group.id])],
        })
        self.assertTrue(folder.with_user(self.prescription_manager).has_write_access, "Prescription manager should have write access on folder")
        self.assertFalse(folder.with_user(self.prescription_user).has_write_access, "Prescription user should not have write access on folder")

    def test_link_constrains(self):
        folder = self.env['prescriptions.folder'].create({'name': 'folder'})
        for url in ("wrong URL format", "https:/ example.com", "test https://example.com"):
            with self.assertRaises(ValidationError):
                self.env['prescriptions.prescription'].create({
                    'name': 'Test Prescription',
                    'folder_id': folder.id,
                    'url': url,
                })
