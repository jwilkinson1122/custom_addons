from odoo import http


class Main(http.Controller):

    @http.route("/pod/catalog", auth="public", website=True)
    def catalog(self, **kwargs):
        Item = http.request.env["pod.item"]
        items = Item.sudo().search([])
        res = http.request.render(
            "pod_portal.item_catalog",
            {"items": items},
        )
        return res
