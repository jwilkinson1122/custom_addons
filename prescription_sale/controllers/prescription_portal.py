from odoo.addons.prescription.controllers.portal import PortalPrescription


class PortalPrescription(PortalPrescription):
    def _get_filter_domain(self, kw):
        res = super()._get_filter_domain(kw)
        if "sale_id" in kw:
            res.append(("order_id", "=", int(kw["sale_id"])))
        return res
