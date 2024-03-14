from odoo import api, models


class EmbroideryBomReport(models.AbstractModel):
    _name = 'report.legion_embroidery.bom_report_view'
    _description = 'Print Job'

    def _get_report_values(self, docids, data=None):
        docs = self.env['embroidery.bom'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'embroidery.bom',
            'docs': docs,
            'proforma': True
        }