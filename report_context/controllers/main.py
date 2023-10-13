import json

from odoo.http import request, route

from odoo.addons.web.controllers import main as report


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report = request.env["ir.actions.report"]._get_report_from_name(reportname)
        original_context = json.loads(data.get("context", "{}") or "{}")
        data["context"] = json.dumps(
            report.with_context(original_context)._get_context()
        )
        return super().report_routes(
            reportname, docids=docids, converter=converter, **data
        )
