from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers import home as web_home
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo import http, _
from odoo.http import request, route
from odoo.service import security
from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import UserError


import logging

_logger = logging.getLogger(__name__)


class HomeExtended(Home):
    @http.route()
    def web_load_menus(self, unique):
        response = super().web_load_menus(unique)
        # On logout & re-login we could see wrong menus being rendered
        # To avoid this, menu http cache must be disabled
        response.headers.remove("Cache-Control")
        return response


# class CustomerHierarchy(http.Controller):

#     @http.route("/check/child", auth="public", type="json", website=True)
#     def check_child(self, **kw):
#         if "id" in kw:
#             if kw["id"]:
#                 partner_id = (
#                     request.env["res.partner"].sudo().search([("id", "=", kw["id"])])
#                 )
#                 ids = partner_id.child_ids.ids
#                 if len(partner_id.child_ids.ids) > 0:
#                     return True
#         return False

#     @http.route("/customer/hierarchy", auth="public", type="json", website=True)
#     def customer_hierarchy(self, **kw):
#         if "id" in kw:
#             if kw["id"]:
#                 partner_id = (
#                     request.env["res.partner"].sudo().search([("id", "=", kw["id"])])
#                 )
#                 ids = partner_id.child_ids.ids
#             return ids
#         return False


class CustomerPortal(CustomerPortal):

    def _prepare_prsit_add_contact_address(self):
        partner = request.env.user.partner_id
        countries = request.env["res.country"].sudo().search([])
        states = request.env["res.country.state"].sudo().search([])
        types = request.env["res.partner"]._fields["type"].selection
        return {
            "partner": partner,
            "countries": countries,
            "states": states,
            "types": types,
        }

    def _prepare_prsit_submit_contact_address(self, kwargs):
        return {
            "type": kwargs.get("type"),
            "name": kwargs.get("name"),
            "email": kwargs.get("email"),
            "mobile": kwargs.get("mobile"),
            "phone": kwargs.get("phone"),
            "street": kwargs.get("street"),
            "city": kwargs.get("city"),
            "zip": kwargs.get("zip"),
            "state_id": int(kwargs.get("state_id")),
            "country_id": int(kwargs.get("country_id")),
            "parent_id": request.env.user.partner_id.id,
        }

    @route(
        ["/my/<string:partner>/contact/add", "/my/contact/add"],
        type="http",
        auth="user",
        website=True,
    )
    def add_prsit_contact_address(self, **kwargs):
        values = self._prepare_prsit_add_contact_address()
        if kwargs.get("type"):
            values.update({"address_type": kwargs.get("type")})
        return request.render("nwpl_odoo_master.add_contact_my_details", values)

    @route(["/my/<string:address_type>/submit"], type="http", auth="user", website=True)
    def submit_prsit_contact(self, **kwargs):
        partner = request.env.user.partner_id
        if kwargs and request.httprequest.method == "POST":
            child_data_vals = self._prepare_prsit_submit_contact_address(kwargs)
            request.env["res.partner"].sudo().create(child_data_vals)
        return request.redirect("/my/account")


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
                    "contact_id",
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


class LoginAs(web_home.Home):

    @http.route("/web/login_as/<int:user_id>", type="http", auth="user", sitemap=False)
    def switch_to_user(self, user_id, **kwargs):  # @UnusedVariable
        uid = request.env.user.id  # @UndefinedVariable
        if request.env.user._is_system():  # @UndefinedVariable
            request.session.impersonate_uid = uid
            uid = request.session.uid = user_id
            # invalidate session token cache as we've changed the uid
            request.env.registry.clear_cache()
            request.session.session_token = security.compute_session_token(
                request.session, request.env
            )

            _logger.info(
                "User %s Logged in as %s"
                % (request.env.user.name, request.env["res.users"].browse(user_id).name)
            )

        return request.redirect(self._login_redirect(uid))

    @http.route("/web/login_back", type="http", auth="user", sitemap=False)
    def switch_back(self, **kwargs):  # @UnusedVariable
        uid = request.env.user.id  # @UndefinedVariable
        if request.session.impersonate_uid:  # @UndefinedVariable
            uid = request.session.uid = (
                request.session.impersonate_uid
            )  # @UndefinedVariable
            request.session.impersonate_uid = False
            # invalidate session token cache as we've changed the uid
            request.env.registry.clear_cache()
            request.session.session_token = security.compute_session_token(
                request.session, request.env
            )

        return request.redirect(self._login_redirect(uid) + "?debug=1")
