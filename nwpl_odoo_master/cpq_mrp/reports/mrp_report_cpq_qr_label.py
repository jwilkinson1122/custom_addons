from odoo import models
from ...cpq.helpers.summary_helper import generate_cpq_qr_payload

class ReportCpqMoQrLabel(models.AbstractModel):
    _name = "report.cpq_mrp.report_cpq_mo_qr_label"
    _description = "CPQ MO QR Label Report"

    def _get_report_values(self, docids, data=None):
        docs = self.env["mrp.production"].browse(docids)
        result = []
        for mo in docs:
            copies = mo.cpq_label_qty or 1
            for _ in range(copies):
                if mo.sale_line_id and mo.sale_line_id.cpq_config_hash:
                    mo.cpq_qr_url = generate_cpq_qr_payload(
                        mo.sale_line_id.order_id.id,
                        mo.sale_line_id.id,
                        mo.sale_line_id.product_template_id.id,
                        config_hash=mo.sale_line_id.cpq_config_hash,
                    )
                result.append(mo)

        return {"docs": result}

