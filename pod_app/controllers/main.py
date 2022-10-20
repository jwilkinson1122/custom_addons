from odoo import http


class Items(http.Controller):

    @http.route("/pod/items")
    def list(self, **kwargs):
        Item = http.request.env["pod.item"]
        items = Item.search([])
        return http.request.render(
            "pod_app.item_list_template",
            {"items": items}
        )
