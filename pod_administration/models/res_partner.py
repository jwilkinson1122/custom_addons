
import base64
import threading

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    is_pod = fields.Boolean(default=False)

    @api.model
    def _get_pod_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []

    @api.model
    def create(self, vals):
        vals_upd = vals.copy()
        for (
            _pod,
            check,
            identifier,
            definition,
        ) in self._get_pod_identifiers():
            if vals_upd.get(check) and not vals_upd.get(identifier):
                vals_upd[identifier] = definition(vals_upd)
        if not vals_upd.get("image_1920"):
            vals_upd["image_1920"] = self._get_partner_default_image(vals_upd)
        return super(Partner, self).create(vals_upd)

    @api.model
    def _get_partner_default_image(self, vals):
        if self._get_default_image_path(vals):
            return self._get_default_pod_image(vals)
        return False

    @api.model
    def _get_default_image_path(self, vals):
        return False

    @api.model
    def _get_default_pod_image(self, vals):
        if getattr(
            threading.currentThread(), "testing", False
        ) or self._context.get("install_mode"):
            return False
        image_path = self._get_default_image_path(vals)
        if not image_path:
            return False
        with open(image_path, "rb") as f:
            image = f.read()
        return base64.b64encode(image)

    @api.model
    def default_pod_fields(self):
        return ["is_pod", "company_type"]

    @api.model
    def default_get(self, fields_list):
        result = super(Partner, self).default_get(fields_list)
        for field in self.default_pod_fields():
            if result.get(field) and self.env.context.get("default_parent_id"):
                result[field] = False
        return result
