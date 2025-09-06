from odoo import models
from ...cpq.helpers.summary_helper import generate_cpq_qr_payload, generate_cpq_order_qr_payload

class ReportMoOverview(models.AbstractModel):
    _inherit = "report.mrp.report_mo_overview"

    def _get_report_values(self, docids, data=None):
        result = super()._get_report_values(docids, data=data)
        docs = result.get("docs", [])

        # 'docs' is a list of dicts like {'id': <mo_id>, ...}
        for d in docs:
            mo = self.env["mrp.production"].browse(d["id"])
            d["cpq_configuration_summary"] = mo.cpq_configuration_summary

            line = mo.sale_line_id
            if line and line.cpq_configuration_json:
                d["cpq_qr_url"] = generate_cpq_qr_payload(
                    line.order_id.id, line.id, line.product_template_id.id,
                    config_hash=line.cpq_config_hash, version=1
                )

            if line and line.order_id:
                d["cpq_order_qr_url"] = generate_cpq_order_qr_payload(line.order_id)

        return result
    
    # def _get_report_values(self, docids, data=None):
    #     result = super()._get_report_values(docids, data=data)
    #     docs = result.get("docs", [])

    #     for doc in docs:
    #         if isinstance(doc, dict):
    #             mo = self.env["mrp.production"].browse(doc["id"])
    #             doc["cpq_configuration_summary"] = mo.cpq_configuration_summary

    #             line = mo.sale_line_id
    #             if line and line.cpq_configuration_json:
    #                 doc["cpq_qr_url"] = generate_cpq_qr_payload(
    #                     line.order_id.id,
    #                     line.id,
    #                     line.product_template_id.id,
    #                     config_hash=line.cpq_config_hash,  
    #                     version=1
    #                 )
                    
    #             if mo.sale_line_id and mo.sale_line_id.order_id:
    #                 order = mo.sale_line_id.order_id
    #                 doc["cpq_order_qr_url"] = generate_cpq_order_qr_payload(order)


    #     return result
