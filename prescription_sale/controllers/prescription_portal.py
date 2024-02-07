

from odoo.addons.prescription.controllers.portal import PrescriptionPortal


class PrescriptionPortal(PrescriptionPortal):
    def _get_filter_domain(self, kw):
        res = super()._get_filter_domain(kw)
        if "sale_id" in kw:
            res.append(("order_id", "=", int(kw["sale_id"])))
        return res
