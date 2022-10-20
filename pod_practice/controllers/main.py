from odoo import http
from odoo.addons.pod_app.controllers.main import Items


class ItemsExtended(Items):

    @http.route()
    def list(self, **kwargs):
        response = super().list(**kwargs)
        if kwargs.get("available"):
            all_items = response.qcontext["items"]
            available_items = all_items.filtered("is_available")
            response.qcontext["items"] = available_items
        return response
