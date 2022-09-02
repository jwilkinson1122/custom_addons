
from odoo import ModuleTestCase


class PodPracticeTestCase(ModuleTestCase):
    '''
    Test NWPL Practice module.
    '''
    module = 'pod_practice'


def suite():
    suite = pod.tests.test_pod.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        PodPracticeTestCase))
    return suite
