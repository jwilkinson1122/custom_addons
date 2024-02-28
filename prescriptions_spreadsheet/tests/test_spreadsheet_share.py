


from .common import SpreadsheetTestCommon
from odoo.exceptions import AccessError
from odoo.tests.common import new_test_user

EXCEL_FILES = [
    {
        "content": '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        "path": "[Content_Types].xml",
    }
]


class SpreadsheetSharing(SpreadsheetTestCommon):
    def test_share_url(self):
        prescription = self.create_spreadsheet()
        share_vals = {
            "prescription_ids": [(6, 0, [prescription.id])],
            "folder_id": prescription.folder_id.id,
            "type": "ids",
            "spreadsheet_shares": [
            {
                "spreadsheet_data": prescription.spreadsheet_data,
                "prescription_id": prescription.id,
                "excel_files": EXCEL_FILES,
            }
        ]
        }
        url = self.env["prescriptions.share"].action_get_share_url(share_vals)
        share = self.env["prescriptions.share"].search(
            [("prescription_ids", "in", prescription.id)]
        )
        self.assertEqual(url, share.full_url)
        spreadsheet_share = share.freezed_spreadsheet_ids
        self.assertEqual(len(spreadsheet_share), 1)
        self.assertEqual(spreadsheet_share.prescription_id, prescription)
        self.assertTrue(spreadsheet_share.excel_export)

    def test_two_spreadsheets_share_url(self):
        prescription1 = self.create_spreadsheet()
        prescription2 = self.create_spreadsheet()
        prescriptions = prescription1 | prescription2
        share_vals = {
            "prescription_ids": [(6, 0, prescriptions.ids)],
            "folder_id": prescription1.folder_id.id,
            "type": "ids",
            "spreadsheet_shares": [
            {
                "spreadsheet_data": prescription1.spreadsheet_data,
                "prescription_id": prescription1.id,
                "excel_files": EXCEL_FILES,
            },
            {
                "spreadsheet_data": prescription2.spreadsheet_data,
                "prescription_id": prescription2.id,
                "excel_files": EXCEL_FILES,
            },
        ]
        }
        url = self.env["prescriptions.share"].action_get_share_url(share_vals)
        share = self.env["prescriptions.share"].search(
            [("prescription_ids", "in", prescriptions.ids)]
        )
        self.assertEqual(url, share.full_url)
        spreadsheet_shares = share.freezed_spreadsheet_ids
        self.assertEqual(len(spreadsheet_shares), 2)

    def test_share_popup(self):
        prescription = self.create_spreadsheet()
        share_vals = {
            "prescription_ids": [(6, 0, [prescription.id])],
            "folder_id": prescription.folder_id.id,
            "type": "ids",
            "spreadsheet_shares": [
                {
                    "spreadsheet_data": prescription.spreadsheet_data,
                    "prescription_id": prescription.id,
                    "excel_files": EXCEL_FILES,
                }
            ]
        }
        action = self.env["prescriptions.share"].open_share_popup(share_vals)
        share = self.env["prescriptions.share"].search(
            [("prescription_ids", "in", prescription.id)]
        )
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_id"], share.id)
        self.assertEqual(action["res_model"], "prescriptions.share")
        spreadsheet_share = share.freezed_spreadsheet_ids
        self.assertEqual(len(spreadsheet_share), 1)
        self.assertEqual(spreadsheet_share.prescription_id, prescription)
        self.assertTrue(spreadsheet_share.excel_export)

    def test_can_create_own(self):
        prescription = self.create_spreadsheet()
        with self.with_user(self.spreadsheet_user.login):
            share = self.share_spreadsheet(prescription)

        shared_spreadsheet = share.freezed_spreadsheet_ids
        self.assertTrue(shared_spreadsheet)
        self.assertTrue(shared_spreadsheet.create_uid, self.spreadsheet_user)

    def test_cannot_read_others(self):
        prescription = self.create_spreadsheet()
        share = self.share_spreadsheet(prescription)
        shared_spreadsheet = share.freezed_spreadsheet_ids
        with self.assertRaises(AccessError):
            shared_spreadsheet.with_user(self.spreadsheet_user).spreadsheet_data

    def test_collaborative_spreadsheet_with_token(self):
        prescription = self.create_spreadsheet()
        share = self.share_spreadsheet(prescription)
        raoul = new_test_user(self.env, login="raoul")
        prescription.folder_id.group_ids = self.env.ref("prescriptions.group_prescriptions_user")
        prescription = prescription.with_user(raoul)
        with self.with_user("raoul"):
            # join without token
            with self.assertRaises(AccessError):
                prescription.join_spreadsheet_session()

            # join with wrong token
            with self.assertRaises(AccessError):
                prescription.join_spreadsheet_session(share.id, "a wrong token")

            # join with token
            token = share.access_token
            data = prescription.join_spreadsheet_session(share.id, token)
            self.assertTrue(data)
            self.assertEqual(data["isReadonly"], False)

            revision = self.new_revision_data(prescription)

            # dispatch revision without token
            with self.assertRaises(AccessError):
                prescription.dispatch_spreadsheet_message(revision)

            # dispatch revision with wrong token
            with self.assertRaises(AccessError):
                prescription.dispatch_spreadsheet_message(
                    revision, share.id, "a wrong token"
                )

            # dispatch revision with token
            token = share.access_token
            accepted = prescription.dispatch_spreadsheet_message(revision, share.id, token)
            self.assertEqual(accepted, True)

            # snapshot without token
            snapshot_revision = {
                "type": "SNAPSHOT",
                "serverRevisionId": prescription.sudo().server_revision_id,
                "nextRevisionId": "snapshot-revision-id",
                "data": {"revisionId": "snapshot-revision-id"},
            }
            with self.assertRaises(AccessError):
                prescription.dispatch_spreadsheet_message(snapshot_revision)

            # snapshot with wrong token
            snapshot_revision = {
                "type": "SNAPSHOT",
                "serverRevisionId": prescription.sudo().server_revision_id,
                "nextRevisionId": "snapshot-revision-id",
                "data": {"revisionId": "snapshot-revision-id"},
            }
            with self.assertRaises(AccessError):
                prescription.dispatch_spreadsheet_message(
                    snapshot_revision, share.id, "a wrong token"
                )

            # snapshot with token
            snapshot_revision = {
                "type": "SNAPSHOT",
                "serverRevisionId": prescription.sudo().server_revision_id,
                "nextRevisionId": "snapshot-revision-id",
                "data": {"revisionId": "snapshot-revision-id"},
            }
            accepted = prescription.dispatch_spreadsheet_message(
                snapshot_revision, share.id, token
            )
            self.assertEqual(accepted, True)

    def test_collaborative_readonly_spreadsheet_with_token(self):
        """Readonly access"""
        prescription = self.create_spreadsheet()
        prescription.folder_id.group_ids = self.env.ref("base.group_system")
        prescription.folder_id.read_group_ids = self.env.ref(
            "prescriptions.group_prescriptions_user"
        )
        with self.with_user(self.spreadsheet_user.login):
            share = self.share_spreadsheet(prescription)

        user = new_test_user(self.env, login="raoul")
        prescription = prescription.with_user(user)
        with self.with_user("raoul"):
            # join without token
            with self.assertRaises(AccessError):
                prescription.join_spreadsheet_session()

            # join with token
            data = prescription.join_spreadsheet_session(share.id, share.access_token)
            self.assertEqual(data["isReadonly"], True)

            revision = self.new_revision_data(prescription)
            # dispatch revision without token
            with self.assertRaises(AccessError):
                prescription.dispatch_spreadsheet_message(revision)

            # dispatch revision with wrong token
            with self.assertRaises(AccessError):
                prescription.dispatch_spreadsheet_message(
                    revision, share.id, "a wrong token"
                )

            # dispatch revision with right token but no write access
            with self.assertRaises(AccessError):
                token = share.access_token
                prescription.dispatch_spreadsheet_message(revision, share.id, token)

            # snapshot without token
            snapshot_revision = {
                "type": "SNAPSHOT",
                "serverRevisionId": prescription.sudo().server_revision_id,
                "nextRevisionId": "snapshot-revision-id",
                "data": r"{}",
            }
            with self.assertRaises(AccessError):
                prescription.dispatch_spreadsheet_message(snapshot_revision)

            # snapshot with token
            snapshot_revision = {
                "type": "SNAPSHOT",
                "serverRevisionId": prescription.sudo().server_revision_id,
                "nextRevisionId": "snapshot-revision-id",
                "data": r"{}",
            }
            with self.assertRaises(AccessError):
                prescription.dispatch_spreadsheet_message(
                    snapshot_revision, share.id, token
                )
