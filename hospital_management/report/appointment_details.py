from odoo import api, models

class ParticularReport(models.AbstractModel):
    _name = 'report.hospital_management.report_hospital_appointment'
    #_name = 'report.report_name'

    def _get_report_values(self, docids, data=None):
        
        print("data", data)
        print("docids", docids)
        model = data['context']['active_model']
        ids = data['context']['active_ids']
        docs = self.env[model].browse(ids)
        return {
            'docs': docs,
            'mode': data['mode']
        }