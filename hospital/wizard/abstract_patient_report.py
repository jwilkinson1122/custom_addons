from odoo import models, api


class AllReport(models.AbstractModel):
    _name = 'report.hospital.report_patient_wizard'
    _description = "create_patient_report_wizard.xml"

    @api.model
    def _get_report_values(self, docids, data=None):
        print("test ...............")
        print(data)
        print(docids)
        return {
            'data': 101
        }
