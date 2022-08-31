

from odoo.tests import TransactionCase


class TestCodification(TransactionCase):
    def test_codification(self):
        code = self.env["podiatry.sct.concept"].create(
            {"code": "001", "name": "Test"}
        )
        self.assertEqual(code.display_name, "[001] Test")

    def test_search(self):
        code = self.env["podiatry.sct.concept"].name_search("138875005")
        self.assertTrue(code)

    def test_multiparents(self):
        sct = self.env["podiatry.sct.concept"]
        root = self.browse_ref("podiatry_terminology_sct.sct_138875005")
        parent = self.browse_ref("podiatry_terminology_sct.sct_105590001")
        code = sct.create(
            {"code": "Test", "name": "Name", "parent_ids": [(4, parent.id)]}
        )
        self.assertGreater(len(code.full_parent_ids), len(code.parent_ids))
        self.assertGreater(len(root.full_child_ids), len(root.child_ids))
