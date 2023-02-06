# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class ProductProduct(models.Model):

    _inherit = "product.product"

    is_device = fields.Boolean("Is Device")
    is_categ_id = fields.Boolean("Is Categ")
    is_service = fields.Boolean("Is Service")

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        args = args or []
        context = self._context or {}
        bookin_date = context.get("bookin_date")
        bookout_date = context.get("bookout_date")
        if isinstance(bookin_date, str):
            bookin_date = fields.datetime.strptime(
                context.get(
                    "bookin_date"), tools.DEFAULT_SERVER_DATETIME_FORMAT
            )
        if isinstance(bookout_date, str):
            bookout_date = fields.datetime.strptime(
                context.get(
                    "bookout_date"), tools.DEFAULT_SERVER_DATETIME_FORMAT
            )
        if bookin_date and bookout_date:
            podiatry_device_obj = self.env["podiatry.device"]
            avail_prod_ids = []
            for device in podiatry_device_obj.search([]):
                assigned = False
                for device_line in device.device_line_ids:
                    if device_line.status != "cancel":
                        if (bookin_date <= device_line.book_in <= bookout_date) or (
                            bookin_date <= device_line.book_out <= bookout_date
                        ):
                            assigned = True
                        elif (
                            device_line.book_in <= bookin_date <= device_line.book_out
                        ) or (device_line.book_in <= bookout_date <= device_line.book_out):
                            assigned = True
                if not assigned:
                    avail_prod_ids.append(device.product_id.id)
            args.append(("id", "in", avail_prod_ids))
        return super(ProductProduct, self)._search(
            args, offset, limit, order, count=count, access_rights_uid=access_rights_uid
        )
