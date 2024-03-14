from odoo import api, models


class EmbroideryReport(models.AbstractModel):
    _name = 'report.legion_embroidery.emb_report_view'
    _description = 'Print Job'

    def _get_report_values(self, docids, data=None):
        docs = self.env['embroidery.embroidery'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'embroidery.embroidery',
            'docs': docs,
            'proforma': True
        }