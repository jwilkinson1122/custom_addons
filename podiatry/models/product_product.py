# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_custom_device = fields.Boolean(default=True, help="True if product is a brace")
    is_otc_device = fields.Boolean(default=False, help="True if product does not require a prescription")  
    is_brace_device = fields.Boolean(default=False,help="True if product is a brace")  
    is_categ_id = fields.Boolean("Is Categ")
    is_accommodation = fields.Boolean("Is Accommodation")
    is_web_pub = fields.Boolean(string='Available On Website')
    model = fields.Char(string='Model')
    
    website_ids = fields.Many2many(
        string='Websites',
        comodel_name='website',
        relation='product_template2website_rel',
        column1='product_id',
        column2='website_id')

    def can_access_from_current_website(self, website_id=False):
        if not website_id:
            website_id = self.env['website'].get_current_website().id
        for product in self:
            if not product.website_ids:
                continue
            if website_id not in product.website_ids.ids:
                return False
        return True

class ProductProduct(models.Model):

    _inherit = "product.product"
    
    # prescription_ids = fields.One2many('podiatry.prescription', 'prescription_id', string='Prescription Records')
   
    product_device_id = fields.Many2one(
        'product.product',
        string='Device ID',
        index=True,
        ondelete='cascade',
        domain=[('is_custom_device', '=', True)],
    )
    prescription_device_ids = fields.One2many('product.product', 'product_device_id', string='Prescription Devices')


    # @api.model
    # def _search(
    #     self,
    #     args,
    #     offset=0,
    #     limit=None,
    #     order=None,
    #     count=False,
    #     access_rights_uid=None,
    # ):
    #     args = args or []
    #     context = self._context or {}
    #     bookin_date = context.get("bookin_date")
    #     bookout_date = context.get("bookout_date")
    #     if isinstance(bookin_date, str):
    #         bookin_date = fields.datetime.strptime(
    #             context.get("bookin_date"), tools.DEFAULT_SERVER_DATETIME_FORMAT
    #         )
    #     if isinstance(bookout_date, str):
    #         bookout_date = fields.datetime.strptime(
    #             context.get("bookout_date"), tools.DEFAULT_SERVER_DATETIME_FORMAT
    #         )
    #     if bookin_date and bookout_date:
    #         podiatry_device_obj = self.env["podiatry.device"]
    #         avail_prod_ids = []
    #         for device in podiatry_device_obj.search([]):
    #             assigned = False
    #             for device_line in device.device_line_ids:
    #                 if device_line.status != "cancel":
    #                     if (bookin_date <= device_line.book_in <= bookout_date) or (
    #                         bookin_date <= device_line.book_out <= bookout_date
    #                     ):
    #                         assigned = True
    #                     elif (
    #                         device_line.book_in <= bookin_date <= device_line.book_out
    #                     ) or (device_line.book_in <= bookout_date <= device_line.book_out):
    #                         assigned = True
    #             if not assigned:
    #                 avail_prod_ids.append(device.product_id.id)
    #         args.append(("id", "in", avail_prod_ids))
    #     return super(ProductProduct, self)._search(
    #         args, offset, limit, order, count=count, access_rights_uid=access_rights_uid
    #     )
