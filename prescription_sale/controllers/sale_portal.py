from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.sale.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):
    @http.route(
        ["/my/orders/<int:order_id>/requestprescription"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def request_prescription(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access(
                "sale.order", order_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        order_obj = request.env["sale.order"]
        wizard_obj = request.env["sale.order.prescription.wizard"].sudo()
        wizard_line_field_types = {
            f: d["type"] for f, d in wizard_obj.line_ids.fields_get().items()
        }
        # Set wizard line vals
        mapped_vals = {}
        custom_vals = {}
        partner_shipping_id = post.pop("partner_shipping_id", False)
        if partner_shipping_id:
            try:
                partner_shipping_id = int(partner_shipping_id)
            except ValueError:
                partner_shipping_id = False
        for name, value in post.items():
            try:
                row, field_name = name.split("-", 1)
                if wizard_line_field_types.get(field_name) == "many2one":
                    value = int(value) if value else False
                mapped_vals.setdefault(row, {}).update({field_name: value})
            # Catch possible form custom fields to add them to the Prescription
            # description values
            except ValueError:
                custom_vals.update({name: value})
        # If no operation is filled, no Prescription will be created
        line_vals = [
            (0, 0, vals) for vals in mapped_vals.values() if vals.get("operation_id")
        ]
        # Create wizard an generate prescription
        order = order_obj.browse(order_id).sudo()
        location_id = order.warehouse_id.prescription_loc_id.id
        # Add custom fields text
        custom_description = ""
        if custom_vals:
            custom_description = r"<br \>---<br \>"
            custom_description += r"<br \>".join(
                ["{}: {}".format(x, y) for x, y in custom_vals.items()]
            )
        wizard = wizard_obj.with_context(active_id=order_id).create(
            {
                "line_ids": line_vals,
                "location_id": location_id,
                "partner_shipping_id": partner_shipping_id,
                "custom_description": custom_description,
            }
        )
        user_has_group_portal = request.env.user.has_group(
            "base.group_portal"
        ) or request.env.user.has_group("base.group_public")
        prescription = wizard.sudo().create_prescription(from_portal=True)
        for rec in prescription:
            rec.origin += _(" (Portal)")
        # Add the user as follower of the created Prescription so they can later view them.
        prescription.message_subscribe([request.env.user.partner_id.id])
        # Subscribe the user to the notification subtype so he receives the confirmation
        # note.
        prescription.message_follower_ids.filtered(
            lambda x: x.partner_id == request.env.user.partner_id
        ).subtype_ids += request.env.ref("prescription.mt_prescription_notification")
        if len(prescription) == 0:
            route = order_sudo.get_portal_url()
        elif len(prescription) == 1:
            route = prescription._get_share_url() if user_has_group_portal else prescription.access_url
        else:
            route = (
                order._get_share_url()
                if user_has_group_portal
                else "/my/prescription?sale_id=%d" % order_id
            )
        return request.redirect(route)

    @http.route(
        ["/my/requestprescription/<int:order_id>"], type="http", auth="public", website=True
    )
    def request_sale_prescription(self, order_id, access_token=None, **kw):
        """Request Prescription on a single page"""
        try:
            order_sudo = self._document_check_access(
                "sale.order", order_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        if order_sudo.state in ("draft", "sent", "cancel"):
            return request.redirect("/my")
        values = {
            "sale_order": order_sudo,
            "page_name": "request_prescription",
            "default_url": order_sudo.get_portal_url(),
            "token": access_token,
            "partner_id": order_sudo.partner_id.id,
        }
        if order_sudo.company_id:
            values["res_company"] = order_sudo.company_id
        return request.render("prescription_sale.request_prescription_single_page", values)
