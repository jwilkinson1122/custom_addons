from odoo import models
from ...cpq.helpers.summary_helper import generate_cpq_qr_payload, generate_cpq_order_qr_payload

class ReportWorkorderCPQ(models.AbstractModel):
    _inherit = "mrp.report_mrp_workorder"

    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data=data)
        docs = res.get("docs", [])  # list of mrp.workorder records

        # Build a small per-doc map we can read in QWeb
        enriched = []
        for wo in docs:
            mo = wo.production_id
            line = mo.sale_line_id

            enriched.append({
                "wo": wo,
                "cpq_configuration_summary": mo.cpq_configuration_summary or "",
                "cpq_qr_url": (
                    generate_cpq_qr_payload(
                        line.order_id.id, line.id, line.product_template_id.id,
                        config_hash=line.cpq_config_hash, version=1
                    ) if line and line.cpq_config_hash else False
                ),
                "cpq_order_qr_url": (
                    generate_cpq_order_qr_payload(line.order_id)
                    if line and line.order_id else False
                ),
            })

        # Replace docs with our dicts so QWeb can use doc['...'] fields
        res["docs"] = enriched
        return res