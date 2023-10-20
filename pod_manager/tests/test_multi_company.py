# -*- coding: utf-8 -*-

from odoo.tests import Form
from odoo.addons.pod_manager.tests.common import TestPodCommon
from odoo.addons.base.models.qweb import QWebException


class TestMultiCompany(TestPodCommon):

    def setUp(self):
        super().setUp()
        self.company_1 = self.env['res.company'].create({'name': 'Opoo'})
        self.company_2 = self.env['res.company'].create({'name': 'Otoo'})
        self.practitioners = self.env['pod.practitioner'].create([
            {'name': 'Bidule', 'company_id': self.company_1.id},
            {'name': 'Machin', 'company_id': self.company_2.id},
        ])
        self.res_users_pod_officer.company_ids = [
            (4, self.company_1.id),
            (4, self.company_2.id),
        ]
        self.res_users_pod_officer.company_id = self.company_1.id
        # flush and invalidate the cache, otherwise a full cache may prevent
        # access rights to be checked
        self.practitioners.flush()
        self.practitioners.invalidate_cache()

