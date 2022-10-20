from odoo.http import route, request
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "item_checkout_count" in counters:
            count = request.env["pod.checkout"].search_count([])
            values["item_checkout_count"] = count
        return values

    @route(
        ["/my/item-checkouts", "/my/item-checkouts/page/<int:page>"],
        auth="user",
        website=True,
    )
    def my_item_checkouts(self, page=1, **kw):
        Checkout = request.env["pod.checkout"]
        domain = []
        # Prepare pager data
        checkout_count = Checkout.search_count(domain)
        pager_data = portal.pager(
            url="/my/item_checkouts",
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
                "page_name": "item-checkouts",
                "default_url": "/my/item-checkouts",
                "pager": pager_data,
            }
        )
        return request.render("pod_portal.my_item_checkouts", values)

    @route(["/my/item-checkout/<model('pod.checkout'):doc>"], auth="user", website=True)
    def portal_my_project(self, doc=None, **kw):
        return request.render("pod_portal.item_checkout", {"doc": doc})
