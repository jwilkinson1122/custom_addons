from odoo.http import route, request
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "prescription_checkout_count" in counters:
            count = request.env["podiatry.checkout"].search_count([])
            values["prescription_checkout_count"] = count
        return values

    @route(
        ["/my/prescription-checkouts", "/my/prescription-checkouts/page/<int:page>"],
        auth="user",
        website=True,
    )
    def my_prescription_checkouts(self, page=1, **kw):
        Checkout = request.env["podiatry.checkout"]
        domain = []
        # Prepare pager data
        checkout_count = Checkout.search_count(domain)
        pager_data = portal.pager(
            url="/my/prescription_checkouts",
            total=checkout_count,
            page=page,
            step=self._items_per_page,
        )
        # Recordset according to pager and domain filter
        checkouts = Checkout.search(
            domain, limit=self._items_per_page, offset=pager_data["offset"]
        )
        # Prepare template values
        values = self._prepare_portal_layout_values()
        values.update(
            {
                "checkouts": checkouts,
                "page_name": "prescription-checkouts",
                "default_url": "/my/prescription-checkouts",
                "pager": pager_data,
            }
        )
        return request.render("podiatry_portal.my_prescription_checkouts", values)

    @route(["/my/prescription-checkout/<model('podiatry.checkout'):doc>"], auth="user", website=True)
    def portal_my_project(self, doc=None, **kw):
        return request.render("podiatry_portal.prescription_checkout", {"doc": doc})
