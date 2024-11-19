# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal


class PrescriptionPortal(portal.CustomerPortal):
    """Provide portal access for partners to view prescriptions, sales orders, and invoices."""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "prescriptions_count" in counters:
            prescriptions_count = (
                request.env["prescription.order"].sudo().search_count([])
            )
            values["prescriptions_count"] = prescriptions_count
        return values

    @http.route(["/my/prescriptions"], type="http", auth="user", website=True)
    def portal_my_prescriptions(self, **kwargs):
        if request.env.ref("base.group_partner_manager") in request.env.user.groups_id:
            domain = []
        elif request.env.ref("base.group_user") in request.env.user.groups_id:
            domain = [
                (
                    "practitioner_id",
                    "=",
                    request.env.user.partner_id.id,
                )
            ]
        else:
            domain = [("patient_id", "=", request.env.user.partner_id.id)]
        prescriptions = request.env["prescription.order"].sudo().search(domain)
        return request.render(
            "nwpl_odoo_master.portal_my_prescriptions",
            {"prescriptions": prescriptions, "page_name": "prescriptions"},
        )

    @http.route(
        ["/view/prescriptions/<int:id>"], type="http", auth="public", website=True
    )
    def view_prescriptions(self, id):
        """View prescriptions based on the provided ID.
        :param id: The ID of the sale order to view.
        :return: Rendered template with sale order details."""
        prescription_order = request.env["prescription.order"].browse(id)
        return request.render(
            "nwpl_odoo_master.prescription_portal_template",
            {
                "prescription_details": prescription_order,
                "page_name": "prescription_order",
            },
        )
