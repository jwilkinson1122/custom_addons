from odoo.addons.cgu_hospital.tests.common import TestCommon
from odoo.tests import tagged
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install', 'library', 'access', 'odooshool')
class TestAccessRights(TestCommon):

    def cgu_hospital_doctor_user_access_rights(self):
        with self.assertRaises(AccessError):
            self.env['cgu_hospital.doctor'].with_user(self.hospital_user).create(
                {'name': 'Test doctor'})
        with self.assertRaises(AccessError):
            self.doctor_demo.with_user(self.hospital_user).unlink()

    # def test_01_library_user_access_rights(self):
    #     with self.assertRaises(AccessError):
    #         self.env['library.book'].with_user(self.library_user).create(
    #             {'name': 'Test Book'})
    #     with self.assertRaises(AccessError):
    #         self.book_demo.with_user(self.library_user).unlink()
    #
    # def test_02_library_admin_access_rights(self):
    #     book = self.env['library.book'].with_user(self.library_admin).create(
    #         {'name': 'Test Book'})
    #     book.with_user(self.library_admin).read()
    #     book.with_user(self.library_admin).write({'name': 'Test Book II'})
    #     book.with_user(self.library_admin).unlink()
