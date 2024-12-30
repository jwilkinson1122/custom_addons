from odoo import models, fields, api

class Followproduct(models.Model):

    _name = 'rlbooks.product.followproduct'
    _description = 'Followproduct'
    _order = 'id'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    def _get_default_main_product_id(self):
        main_product_id = self.env.context.get('default_main_product_id')
        return main_product_id if main_product_id else None
  
    # name = fields.Char(required=False,string='Name')
    main_product_id = fields.Many2one("product.template", string='Main product', ondelete='restrict', required=True, readonly=True, copy=True, default=_get_default_main_product_id, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    follow_product_id = fields.Many2one("product.template", string='Follow product', ondelete='restrict', required=True, readonly=False, copy=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    qty = fields.Float(required=True, string='Amount per product', default=0, tracking=True, copy=True)

    included_in_price = fields.Boolean(required=True, string='Included in price (free)', default=False,readonly=False,store=True, copy=True)

    company_id = fields.Many2one('res.company', 'Company', required=False, index=True, default=lambda self: self.env.company)
