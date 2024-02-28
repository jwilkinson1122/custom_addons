# -*- coding: utf-8 -*-


from datetime import date, timedelta
import base64

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

TEXT = base64.b64encode(bytes("TEST", 'utf-8'))

class TestPrescriptionsFolder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent_folder = cls.env['prescriptions.folder'].create({'name': 'Parent'})
        cls.folder = cls.env['prescriptions.folder'].create({'name': 'Folder', 'parent_folder_id': cls.parent_folder.id})
        cls.child_folder = cls.env['prescriptions.folder'].create({'name': 'Child', 'parent_folder_id': cls.folder.id})
        cls.prescription = cls.env['prescriptions.prescription'].create({
            'datas': TEXT,
            'name': 'file.txt',
            'mimetype': 'text/plain',
            'folder_id': cls.child_folder.id,
        })
        cls.folders = cls.env['prescriptions.folder'] | cls.parent_folder | cls.folder | cls.child_folder

    def test_is_shared(self):
        self.assertFalse(any(folder.is_shared for folder in (self.parent_folder, self.folder, self.child_folder)), "None of the folders should be shared by default")

        share_link = self.env['prescriptions.share'].create({
            'folder_id': self.folder.id,
            'include_sub_folders': False,
            'type': 'domain',
        })
        self.folders._compute_is_shared()

        self.assertTrue(self.folder.is_shared, "The folder should be shared")
        self.assertFalse(any((self.parent_folder.is_shared, self.child_folder.is_shared)), "The parent and child folders should not be shared")

        share_link.write({'include_sub_folders': True})
        self.folders._compute_is_shared()

        self.assertTrue(all((self.folder.is_shared, self.child_folder.is_shared)), "The folder and its children should be shared")
        self.assertFalse(self.parent_folder.is_shared, "The parent folder should not be shared")

        share_link.write({'date_deadline': date.today() + timedelta(days=-1)})
        self.folders._compute_is_shared()

        self.assertFalse(any(folder.is_shared for folder in (self.parent_folder, self.folder, self.child_folder)), "None of the folders should be shared by an expired link")

        share_link.write({'date_deadline': date.today() + timedelta(days=1)})
        self.folders._compute_is_shared()

        self.assertTrue(self.folder.is_shared and self.child_folder.is_shared, "The folder and its children should be shared by a link not yet expired")

    def test_folder_copy(self):
        original_folder = self.env['prescriptions.folder'].create({
            'name': 'Template',
        })
        child_folder = self.env['prescriptions.folder'].create({
            'name': 'Child Folder',
            'parent_folder_id': original_folder.id,
        })
        facet = self.env['prescriptions.facet'].create({
            'name': 'Facet',
            'folder_id': child_folder.id,
        })
        tag_1 = self.env['prescriptions.tag'].create({
            'name': 'Tag 1',
            'facet_id': facet.id,
        })
        tag_2 = self.env['prescriptions.tag'].create({
            'name': 'Tag 2',
            'facet_id': facet.id,
        })
        workflow_rule = self.env['prescriptions.workflow.rule'].create({
            'name': 'Rule',
            'domain_folder_id': child_folder.id,
            'condition_type': 'criteria',
            'required_tag_ids': [Command.link(tag_1.id)],
            'excluded_tag_ids': [Command.link(tag_2.id)],
        })
        self.env['prescriptions.workflow.action'].create({
            'workflow_rule_id': workflow_rule.id,
            'action': 'add',
            'facet_id': facet.id,
            'tag_id': tag_2.id,
        })

        copied_folder = original_folder.copy()
        self.assertEqual(original_folder.name, copied_folder.name, "The copied folder should have the same name as the original")

        self.assertEqual(len(copied_folder.children_folder_ids), 1, "The sub workspaces of the template should also be copied.")
        child_folder_copy = copied_folder.children_folder_ids[0]

        self.assertEqual(len(child_folder_copy.facet_ids), 1, "The copied workspaces should retain their facets.")
        facet_copy = child_folder_copy.facet_ids[0]
        self.assertEqual(facet.name, facet_copy.name, "The copied workspaces should retain their facets.")

        self.assertEqual(len(facet_copy.tag_ids), 2, "The copied facets should retain the same tags.")
        self.assertCountEqual([tag.name for tag in facet.tag_ids], [tag.name for tag in facet_copy.tag_ids], "The copied facets should retain the same tags.")
        tag_1_copy, tag_2_copy = facet_copy.tag_ids

        workflow_rule_copy_search = self.env['prescriptions.workflow.rule'].search([('domain_folder_id', '=', child_folder_copy.id)])
        self.assertEqual(len(workflow_rule_copy_search), 1, "The copied workspaces should retain their workflow rules.")
        workflow_rule_copy = workflow_rule_copy_search[0]
        self.assertEqual(workflow_rule.name, workflow_rule_copy.name, "The copied workspaces should retain their workflow rules.")
        self.assertCountEqual(workflow_rule_copy.required_tag_ids.ids, [tag_1_copy.id], "The copied workflow rules should retain their required tags.")
        self.assertCountEqual(workflow_rule_copy.excluded_tag_ids.ids, [tag_2_copy.id], "The copied workflow rules should retain their excluded tags.")

        workflow_actions = self.env['prescriptions.workflow.action'].search([('workflow_rule_id', '=', workflow_rule_copy.id), ('facet_id', '=', facet_copy.id), ('tag_id', '=', tag_2_copy.id)])
        self.assertEqual(len(workflow_actions), 1, "The actions linked to the workspace should be copied and retain their properties")

    def test_folder_copy_rule_move_folder(self):
        """
        Tests copying a folder with an associated action that moves the prescription
        to a different unrelated folder and adds a tag from that other folder.
        The references to the other folder and its tag should be kept identical.
        """
        original_folder, other_folder = self.env['prescriptions.folder'].create([
            {'name': 'Original Folder'}, {'name': 'Other Folder'},
        ])
        other_folder_facet = self.env['prescriptions.facet'].create({
            'name': 'Other Folder Facet',
            'folder_id': other_folder.id,
        })
        other_folder_tag = self.env['prescriptions.tag'].create({
            'name': 'Other Folder Tag',
            'facet_id': other_folder_facet.id,
        })
        workflow_rule = self.env['prescriptions.workflow.rule'].create({
            'name': 'Rule',
            'domain_folder_id': original_folder.id,
            'condition_type': 'criteria',
            'folder_id': other_folder.id,
        })
        workflow_action = self.env['prescriptions.workflow.action'].create({
            'workflow_rule_id': workflow_rule.id,
            'facet_id': other_folder_facet.id,
            'tag_id': other_folder_tag.id,
        })

        copied_folder = original_folder.copy()
        workflow_rule_copy = self.env['prescriptions.workflow.rule'].search([('domain_folder_id', '=', copied_folder.id)])[0]
        self.assertEqual(workflow_rule.folder_id.id, workflow_rule_copy.folder_id.id, "The value of the folder the prescriptions are moved to should be kept identical.")

        workflow_action_copy = self.env['prescriptions.workflow.action'].search([('workflow_rule_id', '=', workflow_rule_copy.id)])[0]
        self.assertEqual(workflow_action_copy.facet_id.id, workflow_action.facet_id.id, "The value of the facet should be kept identical.")
        self.assertEqual(workflow_action_copy.tag_id.id, workflow_action.tag_id.id, "The value of the tag should be kept identical.")

    def test_folder_copy_ancestor_tag(self):
        """
        Tests copying subfolders with associated workflow actions using tags from ancestor folders.
        If the ancestor is being copied in the same copy, the tags should be changed accordingly.
        Else, the tags should not be set on the copied folder.
        """
        folder = self.env['prescriptions.folder'].create({'name': 'Folder'})
        sub_folder = self.env['prescriptions.folder'].create({
            'name': 'Sub Folder',
            'parent_folder_id': folder.id,
        })
        sub_sub_folder = self.env['prescriptions.folder'].create({
            'name': 'Sub sub folder',
            'parent_folder_id': sub_folder.id,
        })
        folder_facet, sub_folder_facet = self.env['prescriptions.facet'].create([
            {'name': 'Folder facet', 'folder_id': folder.id},
            {'name': 'Sub folder facet', 'folder_id': sub_folder.id},
        ])
        folder_tag, sub_folder_tag = self.env['prescriptions.tag'].create([
            {'name': 'Folder tag', 'facet_id': folder_facet.id},
            {'name': 'Sub folder tag', 'facet_id': sub_folder_facet.id},
        ])
        rule = self.env['prescriptions.workflow.rule'].create({
            'name': 'Rule',
            'domain_folder_id': sub_sub_folder.id,
            'required_tag_ids': [Command.link(folder_tag.id)],
            'excluded_tag_ids': [Command.link(sub_folder_tag.id)],
        })
        self.env['prescriptions.workflow.action'].create([
            {
                'workflow_rule_id': rule.id,
                'action': 'remove',
                'facet_id': folder_facet.id,
                'tag_id': folder_tag.id,
            },
            {
                'workflow_rule_id': rule.id,
                'action': 'add',
                'facet_id': sub_folder_facet.id,
                'tag_id': sub_folder_tag.id,
            },
        ])

        sub_folder_copy = sub_folder.copy()
        sub_folder_facet_copy = sub_folder_copy.facet_ids[0]
        sub_folder_tag_copy = sub_folder_facet_copy.tag_ids[0]
        sub_sub_folder_copy = sub_folder_copy.children_folder_ids[0]
        rule_copy = self.env['prescriptions.workflow.rule'].search([('domain_folder_id', '=', sub_sub_folder_copy.id)])
        action_1_copy = self.env['prescriptions.workflow.action'].search([('workflow_rule_id', '=', rule_copy.id), ('action', '=', 'remove')])
        action_2_copy = self.env['prescriptions.workflow.action'].search([('workflow_rule_id', '=', rule_copy.id), ('action', '=', 'add')])

        self.assertEqual(rule_copy.required_tag_ids.ids, [], "The required tags of the copied rule should be empty.")
        self.assertCountEqual(rule_copy.excluded_tag_ids.ids, sub_folder_tag_copy.ids, "The excluded tags of the copied rule should be updated to use the copied tags of the parent folder.")
        self.assertFalse(action_1_copy.facet_id and action_1_copy.tag_id, "The copy of the first action should have no facet and tag set")
        self.assertEqual((action_2_copy.facet_id.id, action_2_copy.tag_id.id), (sub_folder_facet_copy.id, sub_folder_tag_copy.id), "The facet and tag of the copy of the second action should be updated to use the copied tag and facet of the parent folder.")

    def test_move_folder_with_prescription_to_trash(self):
        folder = self.env['prescriptions.folder'].create({'name': 'Folder'})
        prescription = self.env['prescriptions.prescription'].create({
            'datas': TEXT,
            'name': 'file.txt',
            'mimetype': 'text/plain',
            'folder_id': folder.id,
        })
        folder.action_archive()
        self.assertFalse(folder.active, "Folder should be inactive")
        self.assertFalse(prescription.active, "Prescription should be inactive")

    def test_move_folder_without_prescription_to_trash(self):
        folder = self.env['prescriptions.folder'].create({'name': 'Folder'})
        folder.action_archive()
        self.assertFalse(folder.exists(), "Folder should not exist")

    def test_move_folder_with_sub_folder_and_one_prescription_to_trash(self):
        folder = self.env['prescriptions.folder'].create({'name': 'Folder'})
        child_folder = self.env['prescriptions.folder'].create({'name': 'Folder', 'parent_folder_id': folder.id})
        prescription = self.env['prescriptions.prescription'].create({
            'datas': TEXT,
            'name': 'file.txt',
            'mimetype': 'text/plain',
            'folder_id': child_folder.id,
        })
        # Archive a folder should archive all its child fodlers and prescriptions linked to it
        folder.action_archive()
        self.assertFalse(folder.active, "Folder should be inactive")
        self.assertFalse(child_folder.active, "Folder should be inactive")
        self.assertFalse(prescription.active, "Prescription should be inactive")
        # Unarchive a folder should unarchive all its child fodlers and prescriptions linked to it
        folder.action_unarchive()
        self.assertTrue(folder.active, "Folder should be active")
        self.assertTrue(child_folder.active, "Folder should be active")
        self.assertTrue(prescription.active, "Prescription should be active")

        folder.action_archive()
        self.assertFalse(folder.active, "Folder should be inactive")
        self.assertFalse(child_folder.active, "Folder should be inactive")
        self.assertFalse(prescription.active, "Prescription should be inactive")
        # Unarchive a child folder should unarchive all the prescriptions linked to it and put its
        # parent_folder_id to root
        child_folder.action_unarchive()
        self.assertFalse(folder.active, "Folder should be inactive")
        self.assertTrue(child_folder.active, "Folder should be active")
        self.assertTrue(prescription.active, "Prescription should be active")
        self.assertFalse(child_folder.parent_folder_id, "The parent of the former child folder should be False (root)")

    def test_move_folder_with_sub_folder_and_no_prescriptions_to_trash(self):
        folder = self.env['prescriptions.folder'].create({'name': 'Folder'})
        child_folder = self.env['prescriptions.folder'].create({'name': 'Folder', 'parent_folder_id': folder.id})
        folder_id = folder.id
        child_folder_id = child_folder.id
        folder.action_archive()
        self.assertFalse(self.env["prescriptions.folder"].search([('id', 'in', [folder_id, child_folder_id])]),
                         "Folder and child folder should not exist")

    def test_delete_prescription_with_archived_folder(self):
        # Unlink a archived prescription linked to an archvied folder should unlink the folder as well (Assuming that it is
        # the only prescription contained in the folder)
        folder = self.env['prescriptions.folder'].create({'name': 'Folder'})
        prescription = self.env['prescriptions.prescription'].create({
            'datas': TEXT,
            'name': 'file.txt',
            'mimetype': 'text/plain',
            'folder_id': folder.id,
        })
        folder.action_archive()
        prescription.unlink()
        self.assertFalse(folder.exists(), "Folder should not exist")
        self.assertFalse(prescription.exists(), "Prescription should not exist")

class TestPrescriptionsFolderSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # - Root1
        #    - Child1
        #    - Child2
        # - Root2
        #
        with mute_logger('odoo.models.unlink'):
            cls.env['prescriptions.prescription'].search([]).unlink()
            cls.env['prescriptions.prescription'].flush_model()
            cls.env['prescriptions.folder'].search([]).unlink()

        cls.root_folders = cls.env['prescriptions.folder'].create([
            {'name': 'Root1', 'user_specific': True},
            {'name': 'Root2', 'user_specific': False},
        ])

        cls.children_folders = cls.env['prescriptions.folder'].with_context(create_from_search_panel=True).create([
            {'name': 'Child1', 'parent_folder_id': cls.root_folders[0].id},
            {'name': 'Child2', 'parent_folder_id': cls.root_folders[0].id},
        ])

    def test_initial_sequences(self):
        self.assertEqual(self.root_folders[0].sequence, 10)
        self.assertEqual(self.root_folders[1].sequence, 10)
        self.assertEqual(self.children_folders[0].sequence, 0)
        self.assertEqual(self.children_folders[1].sequence, 0)

    def test_resequence_roots(self):
        # Move Root1 after Root2
        self.root_folders[0].move_folder_to(False, False)
        # Moved folder's sequence should have increased
        self.assertEqual(self.root_folders[0].sequence, 11)
        self.assertEqual(self.root_folders[1].sequence, 10)
        # Children folders' sequence should not have changed
        self.assertEqual(self.children_folders[0].sequence, 0)
        self.assertEqual(self.children_folders[1].sequence, 0)

        # Move Root1 back before Root2
        self.root_folders[0].move_folder_to(False, self.root_folders[1].id)
        # Root2's sequence should have increased
        self.assertEqual(self.root_folders[0].sequence, 10)
        self.assertEqual(self.root_folders[1].sequence, 11)
        # Children folders' sequence should not have changed
        self.assertEqual(self.children_folders[0].sequence, 0)
        self.assertEqual(self.children_folders[1].sequence, 0)

    def test_resequence_children(self):
        # Move Child1 after Child2
        self.children_folders[0].move_folder_to(self.root_folders[0].id, False)
        # Moved folder's sequence should have increased
        self.assertEqual(self.children_folders[0].sequence, 1)
        self.assertEqual(self.children_folders[1].sequence, 0)
        # Root folders' sequence should not have changed
        self.assertEqual(self.root_folders[0].sequence, 10)
        self.assertEqual(self.root_folders[1].sequence, 10)

        # Move Child1 back before Child2
        self.children_folders[0].move_folder_to(self.root_folders[0].id, self.children_folders[1].id)
        # Child2's sequence should have increased
        self.assertEqual(self.children_folders[0].sequence, 0)
        self.assertEqual(self.children_folders[1].sequence, 1)
        # Root folders' sequence should not have changed
        self.assertEqual(self.root_folders[0].sequence, 10)
        self.assertEqual(self.root_folders[1].sequence, 10)

    def test_move_root_to_child(self):
        # Move Root2 under the Root1 (as first child)
        self.root_folders[1].move_folder_to(self.root_folders[0].id, self.children_folders[0].id)
        # Moved folder's sequence should be the smallest of the folder
        self.assertEqual(self.root_folders[1].sequence, 0)
        # Moved folder should now inherit rights of its parent
        self.assertEqual(self.root_folders[1].parent_folder_id.id, self.root_folders[0].id)
        self.assertEqual(self.root_folders[1].user_specific, self.root_folders[0].user_specific)
        # Other children folders should be resequenced
        self.assertEqual(self.children_folders[0].sequence, 1)
        self.assertEqual(self.children_folders[1].sequence, 2)
        # Root1's sequence should not have changed
        self.assertEqual(self.root_folders[0].sequence, 10)
        # Move Root1 under one of its child (not possible, would create a recursion)
        with self.assertRaises(UserError):
            self.root_folders[0].move_folder_to(self.children_folders[0].id, False)

    def test_move_child_to_root(self):
        # Move Child1 between roots (that have the same sequence)
        self.children_folders[0].move_folder_to(False, self.root_folders[1].id)
        # Moved folder's sequence should be between the ones of the roots
        self.assertEqual(self.root_folders[0].sequence, 10)
        self.assertEqual(self.children_folders[0].sequence, 11)
        self.assertEqual(self.root_folders[1].sequence, 12)
        # Child2's sequence should not have changed
        self.assertEqual(self.children_folders[1].sequence, 0)
        # Moved folder should not have any parent anymore
        self.assertFalse(self.children_folders[0].parent_folder_id)

        # Move Child2 before Root1
        self.children_folders[1].move_folder_to(False, self.root_folders[0].id)
        # Moved folder's sequence should be the smallest
        self.assertEqual(self.children_folders[1].sequence, 10)
        self.assertEqual(self.children_folders[0].sequence, 12)
        self.assertEqual(self.root_folders[1].sequence, 13)
        self.assertEqual(self.root_folders[0].sequence, 11)
        # Moved folder should not have any parent anymore
        self.assertFalse(self.children_folders[1].parent_folder_id)
