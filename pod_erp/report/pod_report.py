# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class PrescriptionReport(models.AbstractModel):
    _name = "report.pod_erp.report_pod_prescription"
    _description = "Auxiliar to get the report"

    def _get_prescription_data(self, date_start, date_end):
        total_amount = 0.0
        data_prescription = []
        prescription_obj = self.env["pod.prescription"]
        act_domain = [
            ("book_in_date", ">=", date_start),
            ("book_out_date", "<=", date_end),
        ]
        tids = prescription_obj.search(act_domain)
        for data in tids:
            book_in = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(self, data.book_in_date)
            )
            book_out = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(self, data.book_out_date)
            )
            data_prescription.append(
                {
                    "name": data.name,
                    "partner": data.partner_id.name,
                    "book_in": book_in,
                    "book_out": book_out,
                    "amount": data.amount_total,
                }
            )
            total_amount += data.amount_total
        data_prescription.append({"total_amount": total_amount})
        return data_prescription

    @api.model
    def _get_report_values(self, docids, data):
        model = self.env.context.get("active_model")
        if data is None:
            data = {}
        if not docids:
            docids = data["form"].get("docids")
        prescription_profile = self.env["pod.prescription"].browse(docids)
        date_start = data["form"].get("date_start", fields.Date.today())
        date_end = data["form"].get(
            "date_end",
            str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10],
        )
        return {
            "doc_ids": docids,
            "doc_model": model,
            "data": data["form"],
            "docs": prescription_profile,
            "time": time,
            "prescription_data": self._get_prescription_data(date_start, date_end),
        }
