# -*- coding: utf-8 -*-

import logging
import re
import datetime

from odoo import api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def name_get(self):
        res = super(ProductProduct, self.with_context(customerinfo=True)).name_get()
        return res
    
 
    # @api.model
    # def _name_search(self, name="", operator="ilike", limit=100, name_get_uid=None, **kwargs):
    #     res = super(ProductProduct, self)._name_search(name, operator=operator, limit=limit, name_get_uid=name_get_uid)
    #     res_ids = [rec_id for rec_id, rec_name in res]
        
    #     if not self.env.context.get("partner_id") or not name or len(res_ids) >= (limit or 0):
    #         return res
        
    #     remaining_limit = limit - len(res_ids) if limit else limit
        
    #     customerinfo_domain = [
    #         ("partner_id", "=", self.env.context.get("partner_id")),
    #         "|", ("product_code", operator, name), ("product_name", operator, name),
    #     ]
        
    #     customerinfo_ids = self.env["product.customerinfo"]._search(
    #         customerinfo_domain, limit=remaining_limit, access_rights_uid=name_get_uid, **kwargs
    #     )
        
    #     if not customerinfo_ids:
    #         return res
        
    #     customer_product_tmpls = self.env["product.customerinfo"].browse(customerinfo_ids).mapped("product_tmpl_id")
    #     excluded_templates = self.browse(res_ids).mapped("product_tmpl_id")
    #     new_product_tmpls = customer_product_tmpls - excluded_templates
        
    #     new_product_ids = self._search(
    #         [("product_tmpl_id", "in", new_product_tmpls.ids)], limit=remaining_limit, access_rights_uid=name_get_uid, **kwargs
    #     )
        
    #     res.extend([(pid, self.browse(pid).name_get()[0][1]) for pid in new_product_ids])
    #     return res
    
    # @api.model
    # def _name_search(self, name="", args=None, operator="ilike", limit=100, name_get_uid=None):
    #     res = super(ProductProduct, self)._name_search(
    #         name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
    #     )
    #     res_ids = list(res)
    #     res_ids_len = len(res_ids)
    #     if not limit or res_ids_len >= limit:
    #         limit = (limit - res_ids_len) if limit else False
    #     if (
    #         not name
    #         and limit
    #         or not self._context.get("partner_id")
    #         or res_ids_len >= limit
    #     ):
    #         return res_ids
    #     limit -= res_ids_len
    #     customerinfo_ids = self.env["product.customerinfo"]._search(
    #         [
    #             ("partner_id", "=", self._context.get("partner_id")),
    #             "|",
    #             ("product_code", operator, name),
    #             ("product_name", operator, name),
    #         ],
    #         limit=limit,
    #         access_rights_uid=name_get_uid,
    #     )
    #     if not customerinfo_ids:
    #         return res_ids
    #     res_templates = self.browse(res_ids).mapped("product_tmpl_id")
    #     product_tmpls = (
    #         self.env["product.customerinfo"]
    #         .browse(customerinfo_ids)
    #         .mapped("product_tmpl_id")
    #         - res_templates
    #     )
    #     product_ids = list(
    #         self._search(
    #             [("product_tmpl_id", "in", product_tmpls.ids)],
    #             limit=limit,
    #             access_rights_uid=name_get_uid,
    #         )
    #     )
    #     res_ids.extend(product_ids)
    #     return res_ids

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            partner_id = self._context.get('partner_id')
            partners = [partner_id]
            if partner_id:
                if partner := self.env['res.partner'].browse(partner_id):
                    if partner.child_ids:
                        partners.extend(
                            child.id for child in partner.child_ids)
                    if partner.parent_id:
                        partners.append(partner.parent_id.id)
                        if partner.parent_id.child_ids:
                            partners.extend(
                                child.id for child in partner.parent_id.child_ids)
                if customer_ids := self.env['product.customerinfo']._search([('name', 'in', partners), '|', ('product_code', operator, name), ('product_name', operator, name)], order=order):
                    return self._search(
                        [('product_tmpl_id.customer_ids', 'in', customer_ids)], limit=limit, order=order)
            if operator in positive_operators:
                product_ids = list(self._search(
                    [('default_code', '=', name)] + domain, limit=limit, order=order)) or list(self._search(
                        [('barcode', '=', name)] + domain, limit=limit, order=order))
            if not product_ids:
                if operator not in expression.NEGATIVE_TERM_OPERATORS:
                    product_ids = list(self._search(
                        domain + [('default_code', operator, name)], limit=limit, order=order))
                    if not limit or len(product_ids) < limit:
                        limit2 = (limit - len(product_ids)) if limit else False
                        product2_ids = self._search(
                            domain + [('name', operator, name), ('id', 'not in', product_ids)], limit=limit2, order=order)
                        product_ids.extend(product2_ids)
                else:
                    domain2 = expression.OR([
                        ['&', ('default_code', operator, name),
                         ('name', operator, name)],
                        ['&', ('default_code', '=', False),
                         ('name', operator, name)],
                    ])
                    domain2 = expression.AND([domain, domain2])
                    product_ids = list(self._search(
                        domain2, limit=limit, order=order))
            if not product_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                if res := ptrn.search(name):
                    product_ids = list(self._search(
                        [('default_code', '=', res.group(2))] + domain, limit=limit, order=order))
            if not product_ids and self._context.get('partner_id'):
                if suppliers_ids := self.env['product.supplierinfo']._search(
                    [
                        ('partner_id', '=', self._context.get('partner_id')),
                        '|',
                        ('product_code', operator, name),
                        ('product_name', operator, name),
                    ]
                ):
                    product_ids = self._search(
                        [('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit, order=order)
        else:
            product_ids = self._search(domain, limit=limit, order=order)
        return product_ids



    def _get_price_from_customerinfo(self, partner_id):
        self.ensure_one()
        if not partner_id:
            return 0.0
        partner = self.env["res.partner"].browse(partner_id)
        customerinfo = self._select_customerinfo(partner=partner)
        if customerinfo:
            return customerinfo.price
        return 0.0

    def price_compute(
        self, price_type, uom=False, currency=False, company=None, date=False
    ):
        if price_type == "partner":
            partner_id = self.env.context.get(
                "partner_id", False
            ) or self.env.context.get("partner", False)
            if partner_id and isinstance(partner_id, models.BaseModel):
                partner_id = partner_id.id
            prices = super().price_compute(
                "list_price", uom, currency, company, date=date
            )
            for product in self:
                price = product._get_price_from_customerinfo(partner_id)
                if not price:
                    continue
                prices[product.id] = price
                if not uom and self._context.get("uom"):
                    uom = self.env["uom.uom"].browse(self._context["uom"])
                if not currency and self._context.get("currency"):
                    currency = self.env["res.currency"].browse(
                        self._context["currency"]
                    )
                if uom:
                    prices[product.id] = product.uom_id._compute_price(
                        prices[product.id], uom
                    )
                if currency:
                    date = self.env.context.get("date", datetime.datetime.now())
                    prices[product.id] = product.currency_id._convert(
                        prices[product.id], currency, company, date
                    )
            return prices
        return super().price_compute(price_type, uom, currency, company, date=date)

    def _prepare_domain_customerinfo(self, params):
        self.ensure_one()
        partner_id = params.get("partner_id")
        return [
            ("partner_id", "=", partner_id),
            "|",
            ("product_id", "=", self.id),
            "&",
            ("product_tmpl_id", "=", self.product_tmpl_id.id),
            ("product_id", "=", False),
        ]

    def _select_customerinfo(
        self, partner=False, _quantity=0.0, _date=None, _uom_id=False, params=False
    ):
        """Customer version of the standard `_select_seller`."""
        # TODO: For now it is just the function name with same arguments, but
        #  can be changed in future migrations to be more in line Odoo
        #  standard way to select supplierinfo's.
        if not params:
            params = dict()
        params.update({"partner_id": partner.id})
        domain = self._prepare_domain_customerinfo(params)
        res = (
            self.env["product.customerinfo"]
            .search(domain)
            .sorted(lambda s: (s.sequence, s.min_qty, s.price, s.id))
        )
        res_1 = res.sorted("product_tmpl_id")[:1]
        return res_1
