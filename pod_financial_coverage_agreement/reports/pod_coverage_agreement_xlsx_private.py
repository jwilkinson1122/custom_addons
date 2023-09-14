from odoo import models


class PodiatryCoverageAgreementXlsx(models.AbstractModel):
    _name = "report.pod_financial_coverage_agreement.mca_xlsx_private"
    _inherit = "report.pod_financial_coverage_agreement.mca_xlsx"
    _description = "Report NWP Podiatry Financial Coverage Agreement Private"
    _private_report = True
