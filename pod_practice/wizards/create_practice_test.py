#############################################################################
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import MissingError
import requests
import json
import datetime


# __all__ = ['CreatePracticeTestOrderInit', 'CreatePracticeTestOrder', 'RequestTest',
#     'RequestPatientPracticeTestStart', 'RequestPatientPracticeTest']


# class CreatePracticeTestOrderInit(ModelView):
#     'Create Test Report Init'
#     _name = 'pod.practice.test.create.init'


class CreatePracticeTestOrder(models.TransientModel):
    _name = 'pod.practice.test.create'
    _description = 'Create Practice Test Report'

    start = StateView('pod.practice.test.create.init',
                      'pod_practice.view_practice_make_test', [
                          Button('Cancel', 'end', 'pod-cancel'),
                          Button('Create Test Order',
                                 'create_practice_test', 'pod-ok', True),
                      ])

    create_practice_test = StateTransition()

    def transition_create_practice_test(self):
        TestRequest = Pool().get('pod.patient.practice.test')
        Practice = Pool().get('pod.practice')

        tests_report_data = []

        tests = TestRequest.browse(Transaction().context.get('active_ids'))

        for practice_test_order in tests:

            test_cases = []
            test_report_data = {}

            if practice_test_order.state == 'ordered':
                self.raise_user_error(
                    "The Practice test order is already created")

            test_report_data['test'] = practice_test_order.name.id
            test_report_data['patient'] = practice_test_order.patient_id.id
            if practice_test_order.doctor_id:
                test_report_data['requestor'] = practice_test_order.doctor_id.id
            test_report_data['date_requested'] = practice_test_order.date
            test_report_data['request_order'] = practice_test_order.request

            for critearea in practice_test_order.name.critearea:
                test_cases.append(('create', [{
                    'name': critearea.name,
                    'sequence': critearea.sequence,
                    'lower_limit': critearea.lower_limit,
                    'upper_limit': critearea.upper_limit,
                    'normal_range': critearea.normal_range,
                    'units': critearea.units and critearea.units.id,
                }]))
            test_report_data['critearea'] = test_cases

            tests_report_data.append(test_report_data)

        Practice.create(tests_report_data)
        TestRequest.write(tests, {'state': 'ordered'})

        return 'end'


class RequestTest(ModelView):
    'Request - Test'
    _name = 'pod.request-test'
    _table = 'pod_request_test'

    request = fields.Many2One('pod.patient.practice.test.request.start',
                              'Request', required=True)
    test = fields.Many2One('pod.practice.test_type', 'Test', required=True)


class RequestPatientPracticeTestStart(ModelView):
    'Request Patient Practice Test Start'
    _name = 'pod.patient.practice.test.request.start'

    date = fields.DateTime('Date')
    patient = fields.Many2One('pod.patient', 'Patient', required=True)
    doctor = fields.Many2One('pod.medicalprofessional', 'Doctor',
                             help="Doctor who Request the practice tests.")
    tests = fields.Many2Many('pod.request-test', 'request', 'test',
                             'Tests', required=True)
    urgent = fields.Boolean('Urgent')

    @staticmethod
    def default_date():
        return datetime.now()

    @staticmethod
    def default_patient():
        if Transaction().context.get('active_model') == 'pod.patient':
            return Transaction().context.get('active_id')

    @staticmethod
    def default_doctor():
        pool = Pool()
        HealthProf = pool.get('pod.medicalprofessional')
        hp = HealthProf.get_pod_professional()
        if not hp:
            RequestPatientPracticeTestStart.raise_user_error(
                "No medical professional associated to this user !")
        return hp


class RequestPatientPracticeTest(models.TransientModel):
    _name = 'pod.patient.practice.test.request'
    _description = 'Request Patient Practice Test'

    start = StateView('pod.patient.practice.test.request.start',
                      'pod_practice.patient_practice_test_request_start_view_form', [
                          Button('Cancel', 'end', 'pod-cancel'),
                          Button('Request', 'request',
                                 'pod-ok', default=True),
                      ])
    request = StateTransition()

    def transition_request(self):
        PatientPracticeTest = Pool().get('pod.patient.practice.test')
        Sequence = Pool().get('ir.sequence')
        Config = Pool().get('pod.sequences')

        config = Config(1)
        request_number = Sequence.get_id(config.practice_request_sequence.id)
        practice_tests = []
        for test in self.start.tests:
            practice_test = {}
            practice_test['request'] = request_number
            practice_test['name'] = test.id
            practice_test['patient_id'] = self.start.patient.id
            if self.start.doctor:
                practice_test['doctor_id'] = self.start.doctor.id
            practice_test['date'] = self.start.date
            practice_test['urgent'] = self.start.urgent
            practice_tests.append(practice_test)
        PatientPracticeTest.create(practice_tests)

        return 'end'
