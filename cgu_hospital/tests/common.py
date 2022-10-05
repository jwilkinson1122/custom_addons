from odoo.tests.common import TransactionCase


class TestCommon(TransactionCase):

    def setUp(self):
        super(TestCommon, self).setUp()

        self.group_hospital_user = self.env.ref(
            'cgu_hospital.group_hospital_user')

        self.group_hospital_admin = self.env.ref(
            'cgu_hospital.group_hospital_admin')

        self.hospital_user = self.env['res.users'].create({
            'name': 'hospital User',
            'login': 'hospital_user',
            'groups_id': [(4, self.env.ref('base.group_user').id),
                          (4, self.group_hospital_user.id)],
        })

        self.hospital_admin = self.env['res.users'].create({
            'name': 'hospital Admin',
            'login': 'hospital_admin',
            'groups_id': [(4, self.env.ref('base.group_user').id),
                          (4, self.group_hospital_admin.id)],
        })

        self.reader = self.env['res.partner'].create({'name': 'Demo Reader'})

        self.doctor_demo = self.env['cgu_hospital.doctor'].create({
            'name': 'Demo doctor'})
