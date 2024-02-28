# -*- coding: utf-8 -*-

from .common import SpreadsheetTestCommon, TEST_CONTENT
from odoo.exceptions import AccessError
from odoo.tests.common import new_test_user

class SpreadsheetTemplate(SpreadsheetTestCommon):

    def test_copy_template_without_name(self):
        template = self.env["spreadsheet.template"].create({
            "spreadsheet_data": TEST_CONTENT,
            "name": "Template name",
        })
        self.assertEqual(
            template.copy().name,
            "Template name (copy)",
            "It should mention the template is a copy"
        )

    def test_copy_template_with_name(self):
        template = self.env["spreadsheet.template"].create({
            "spreadsheet_data": TEST_CONTENT,
            "name": "Template name",
        })
        self.assertEqual(
            template.copy({"name": "New Name"}).name,
            "New Name",
            "It should have assigned the given name"
        )

    def test_allow_write_on_own_template(self):
        template = self.env["spreadsheet.template"].with_user(self.spreadsheet_user)\
            .create({
                "spreadsheet_data": TEST_CONTENT,
                "name": "Template name",
            })
        template.write({"name": "bye"})
        self.assertEqual(
            template.name,
            "bye",
            "Prescription User can edit their own templates"
        )

    def test_forbid_write_on_others_template(self):
        template = self.env["spreadsheet.template"].create({
            "spreadsheet_data": TEST_CONTENT,
            "name": "Template name",
        })
        with self.assertRaises(
            AccessError, msg="Prescription User cannot edit other's templates"
        ):
            template.with_user(self.spreadsheet_user).write(
                {"name": "bye"}
            )

    def test_action_create_spreadsheet(self):
        template = self.env["spreadsheet.template"].create({
            "spreadsheet_data": TEST_CONTENT,
            "name": "Template name",
        })
        commands = self.new_revision_data(template)
        template.dispatch_spreadsheet_message(commands)
        action = template.action_create_spreadsheet()
        spreadsheet_id = action["params"]["spreadsheet_id"]
        prescription = self.env["prescriptions.prescription"].browse(spreadsheet_id)
        self.assertTrue(prescription.exists())
        self.assertEqual(prescription.handler, "spreadsheet")
        self.assertEqual(prescription.mimetype, "application/o-spreadsheet")
        self.assertEqual(prescription.name, "Template name")
        self.assertEqual(prescription.spreadsheet_data, TEST_CONTENT)
        self.assertEqual(
            len(prescription.spreadsheet_revision_ids),
            2,
            "it should have copied the revision and added the user locale revision"
        )
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "action_open_spreadsheet")
        self.assertTrue(action["params"]["convert_from_template"])

    def test_action_create_spreadsheet_non_admin(self):
        user = new_test_user(
            self.env, login="Jean", groups="prescriptions.group_prescriptions_user"
        )
        template = self.env["spreadsheet.template"].create({
            "spreadsheet_data": TEST_CONTENT,
            "name": "Template name",
        })
        commands = self.new_revision_data(template)
        template.dispatch_spreadsheet_message(commands)
        action = template.with_user(user).action_create_spreadsheet()
        spreadsheet_id = action["params"]["spreadsheet_id"]
        prescription = self.env["prescriptions.prescription"].browse(spreadsheet_id)
        self.assertTrue(prescription.exists())
        self.assertEqual(
            len(prescription.spreadsheet_revision_ids),
            2,
            "it should have copied the revision and added the user locale revision"
        )

    def test_action_create_spreadsheet_with_user_locale(self):
        self.env.ref("base.lang_fr").active = True
        user = self.spreadsheet_user
        user.lang = "fr_FR"
        template = self.env["spreadsheet.template"].create({
            "name": "Template name",
        })
        action = template.with_user(user).action_create_spreadsheet()
        spreadsheet_id = action["params"]["spreadsheet_id"]
        prescription = self.env["prescriptions.prescription"].browse(spreadsheet_id)
        revision = prescription.join_spreadsheet_session()["revisions"]
        self.assertEqual(len(revision), 1)
        self.assertEqual(revision[0]["commands"][0]["type"], "UPDATE_LOCALE")
        self.assertEqual(revision[0]["commands"][0]["locale"]["code"], "fr_FR")

    def test_action_create_spreadsheet_with_existing_revision_with_user_locale(self):
        self.env.ref("base.lang_fr").active = True
        user = self.spreadsheet_user
        user.lang = "fr_FR"
        template = self.env["spreadsheet.template"].create({
            "name": "Template name",
        })
        template.dispatch_spreadsheet_message(self.new_revision_data(template))
        action = template.with_user(user).action_create_spreadsheet()
        spreadsheet_id = action["params"]["spreadsheet_id"]
        prescription = self.env["prescriptions.prescription"].browse(spreadsheet_id)
        revision = prescription.join_spreadsheet_session()["revisions"]
        self.assertEqual(len(revision), 2)
        self.assertEqual(revision[-1]["commands"][0]["type"], "UPDATE_LOCALE")
        self.assertEqual(revision[-1]["commands"][0]["locale"]["code"], "fr_FR")

    def test_action_create_spreadsheet_in_folder(self):
        template = self.env["spreadsheet.template"].create({
            "spreadsheet_data": TEST_CONTENT,
            "name": "Template name",
        })
        action = template.action_create_spreadsheet({
            "folder_id": self.folder.id
        })
        spreadsheet_id = action["params"]["spreadsheet_id"]
        prescription = self.env["prescriptions.prescription"].browse(spreadsheet_id)
        self.assertEqual(prescription.folder_id, self.folder)

    def test_join_template_session(self):
        template = self.env["spreadsheet.template"].create({
            "spreadsheet_data": TEST_CONTENT,
            "name": "Template name",
        })
        data = template.join_spreadsheet_session()
        self.assertEqual(data["data"], {})
        self.assertEqual(data["revisions"], [], "It should not have any initial revisions")

    def test_join_active_template_session(self):
        template = self.env["spreadsheet.template"].create({
            "spreadsheet_data": TEST_CONTENT,
            "name": "Template name",
        })
        commands = self.new_revision_data(template)
        template.dispatch_spreadsheet_message(commands)
        template = template.join_spreadsheet_session()
        del commands["clientId"]
        self.assertEqual(template["data"], {})
        self.assertEqual(template["revisions"], [commands], "It should have any initial revisions")
