from odoo.http import route, request
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "prescription_bookout_count" in counters:
            count = request.env["pod.bookout"].search_count([])
            values["prescription_bookout_count"] = count
        return values

    @route(
        ["/my/prescription-bookouts", "/my/prescription-bookouts/page/<int:page>"],
        auth="user",
        website=True,
    )
    def my_prescription_bookouts(self, page=1, **kw):
        Bookout = request.env["pod.bookout"]
        domain = []
        # Prepare pager data
        bookout_count = Bookout.search_count(domain)
        pager_data = portal.pager(
            url="/my/prescription_bookouts",
            total=bookout_count,
            page=page,
            step=self._items_per_page,
        )
        # Recordset according to pager and domain filter
        bookouts = Bookout.search(
            domain, limit=self._items_per_page, offset=pager_data["offset"]
        )
        # Prepare template values
        values = self._prepare_portal_layout_values()
        values.update(
            {
                "bookouts": bookouts,
                "page_name": "prescription-bookouts",
                "default_url": "/my/prescription-bookouts",
                "pager": pager_data,
            }
        )
        return request.render("pod_portal.my_prescription_bookouts", values)

    @route(["/my/prescription-bookout/<model('pod.bookout'):doc>"], auth="user", website=True)
    def portal_my_project(self, doc=None, **kw):
        return request.render("pod_portal.prescription_bookout", {"doc": doc})
