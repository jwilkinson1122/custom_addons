# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class ProductProduct(models.Model):

    _inherit = "product.product"

    is_device = fields.Boolean("Is Device")
    is_cate_gid = fields.Boolean("Is Categ")
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
        book_in_date = context.get("book_in_date")
        book_out_date = context.get("book_out_date")
        if isinstance(book_in_date, str):
            book_in_date = fields.datetime.strptime(
                context.get("book_in_date"), tools.DEFAULT_SERVER_DATETIME_FORMAT
            )
        if isinstance(book_out_date, str):
            book_out_date = fields.datetime.strptime(
                context.get("book_out_date"), tools.DEFAULT_SERVER_DATETIME_FORMAT
            )
        if book_in_date and book_out_date:
            account_device_obj = self.env["account.device"]
            avail_prod_ids = []
            for device in account_device_obj.search([]):
                assigned = False
                for rm_line in device.device_line_ids:
                    if rm_line.status != "cancel":
                        if (book_in_date <= rm_line.book_in <= book_out_date) or (
                            book_in_date <= rm_line.book_out <= book_out_date
                        ):
                            assigned = True
                        elif (
                            rm_line.book_in <= book_in_date <= rm_line.book_out
                        ) or (rm_line.book_in <= book_out_date <= rm_line.book_out):
                            assigned = True
                if not assigned:
                    avail_prod_ids.append(device.product_id.id)
            args.append(("id", "in", avail_prod_ids))
        return super(ProductProduct, self)._search(
            args, offset, limit, order, count=count, access_rights_uid=access_rights_uid
        )
