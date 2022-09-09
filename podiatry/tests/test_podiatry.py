# See LICENSE file for full copyright and licensing details.

from odoo.tests import common


class TestPodiatry(common.TransactionCase):

    def setUp(self):
        super(TestPodiatry, self).setUp()
        self.patient_patient_obj = self.env['patient.patient']
        self.doctor_obj = self.env['podiatry.doctor']
        self.parent_obj = self.env['podiatry.parent']
        self.podiatry_podiatry_obj = self.env['podiatry.podiatry']
        self.podiatry_standard_obj = self.env['podiatry.standard']
        self.res_company_obj = self.env['res.company']
        self.assign_roll_obj = self.env['assign.roll.no']
        self.account_id = self.env.ref('podiatry.demo_podiatry_1')
        self.standard_medium = self.env.ref('podiatry.demo_standard_medium_1')
        self.year = self.env.ref('podiatry.demo_academic_year_2')
        self.currency_id = self.env.ref('base.INR')
        self.sch = self.env.ref('podiatry.demo_podiatry_1')
        self.country_id = self.env.ref('base.in')
        self.std = self.env.ref('podiatry.demo_standard_standard_1')
        self.state_id = self.env.ref('base.state_in_gj')
        self.subject1 = self.env.ref('podiatry.demo_subject_subject_1')
        self.subject2 = self.env.ref('podiatry.demo_subject_subject_2')
        self.patient_patient = self.env.ref('podiatry.demo_patient_patient_2')
        self.patient_done = self.env.ref('podiatry.demo_patient_patient_6')
        self.parent = self.env.ref('podiatry.demo_patient_parent_1')
        patient_list = [self.patient_done.id]
        self.patient_patient._compute_patient_age()
        self.patient_patient.check_age()
        self.patient_patient.register_done()
        self.patient_patient.set_archive()
        self.parent.patient_id = [(6, 0, patient_list)]
        # Create academic Year
        self.academic_year_obj = self.env['academic.year']
        self.academic_year = self.academic_year_obj.\
            create({'sequence': 7,
                    'code': '2012',
                    'name': '2012 Year',
                    'date_start': '2012-01-01',
                    'date_stop': '2012-12-31'
                    })
        self.academic_year._check_academic_year()
        self.academic_month_obj = self.env['academic.month']
        # Academic month created
        self.academic_month = self.academic_month_obj.\
            create({'name': 'May',
                    'code': 'may',
                    'date_start': '2012-05-01',
                    'date_stop': '2012-05-31',
                    'year_id': self.academic_year.id
                    })
        self.academic_month._check_duration()
        self.academic_month._check_year_limit()
        self.assign_roll_no = self.assign_roll_obj.\
            create({'standard_id': self.std.id,
                    'medium_id': self.standard_medium.id
                    })
        self.assign_roll_no.assign_rollno()

    def test_podiatry(self):
        self.assertEqual(self.patient_patient.account_id,
                         self.patient_patient.standard_id.account_id)
