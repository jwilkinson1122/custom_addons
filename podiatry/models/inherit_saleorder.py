# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class InheritedSaleOrder(models.Model):
    _inherit = 'sale.order'

    prescription_id = fields.Many2one('podiatry.prescription')
    practice_id = fields.Char(related='prescription_id.practice_id.name')
    practitioner_id = fields.Char(
        related='prescription_id.practitioner_id.name')
    patient_id = fields.Char(related='prescription_id.patient_id.name')
    prescription_date = fields.Date(
        related='prescription_id.prescription_date')
    purchase_order_count = fields.Char()
    po_ref = fields.Many2one('purchase.order', string='PO Ref')

    def action_config_start(self):
        """Return action to start configuration wizard"""
        configurator_obj = self.env["product.configurator.sale"]
        ctx = dict(
            self.env.context, default_order_id=self.id, wizard_model="product.configurator.sale", allow_preset_selection=True,
        )
        return configurator_obj.with_context(ctx).get_wizard_action()

    def print_prescription_report_ticket_size(self):
        return self.env.ref("podiatry.practitioner_prescription_ticket_size2").report_action(self.prescription_id)

    def print_podiatry_prescription_report_ticket_size(self):
        return self.env.ref("podiatry.practitioner_prescription_ticket_size2").report_action(self.prescription_id)

    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(
                rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(
        string="This sale order is approved for the sum of: ", compute='_compute_amount_in_word')

    def print_sale_order_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "podiatry.sale_order_report",
            'report_file': "podiatry.sale_order_report",
            'report_type': 'qweb-pdf',
        }

    def print_prescription_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "podiatry.sale_prescription_template",
            'report_file': "podiatry.sale_prescription_template",
            'report_type': 'qweb-pdf'
        }

    # def print_purchase_order_report(self):
    #     return {
    #         'type': 'ir.actions.report',
    #         'report_name': "podiatry.purchase_order_report",
    #         'report_file': "podiatry.purchase_order_report",
    #         'report_type': 'qweb-pdf',
    #     }

    @api.onchange('prescription_id')
    def test(self):
        product = self.env.ref('podiatry.podiatry_product')
        self.order_line = None
        if self.prescription_id.examination_chargeable == True:
            self.order_line |= self.order_line.new({
                'name': '',
                'product_id': product.id,
                'product_uom_qty': 1,
                'qty_delivered': 1,
                'product_uom': '',
                'price_unit': '',

            })

    # @api.model
    # def create(self,vals):
    #     order_line_product = [(0, 0, {'product_id':30,'partner_invoice_id':12,'partner_id':12})]
    #
    #     vals = {
    #
    #         'order_line': order_line_product,
    #
    #     }
    #     result = super(InheritedSaleOrder,self).create(vals)
    #     return result

    def print_prescription_report(self):
        pass

    def print_prescription_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "podiatry.sale_prescription_template",
            'report_file': "podiatry.sale_prescription_template",
            'report_type': 'qweb-pdf'
        }


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _prepare_from_pos(self, sale_order, order_line_data):
        ProductProduct = self.env["product.product"]
        product = ProductProduct.browse(order_line_data["product_id"])
        return {
            "order_id": sale_order.id,
            "product_id": order_line_data["product_id"],
            "name": product.name,
            "product_uom_qty": order_line_data["qty"],
            "discount": order_line_data["discount"],
            "price_unit": order_line_data["price_unit"],
            "tax_id": order_line_data["tax_ids"],
        }

    custom_value_ids = fields.One2many(comodel_name="product.config.session.custom.value", inverse_name="cfg_session_id", related="config_session_id.custom_value_ids", string="Configurator Custom Values",
                                       )
    config_ok = fields.Boolean(related="product_id.config_ok", string="Configurable", readonly=True
                               )
    config_session_id = fields.Many2one(comodel_name="product.config.session", string="Config Session"
                                        )

    def reconfigure_product(self):
        """Creates and launches a product configurator wizard with a linked
        template and variant in order to re-configure a existing product. It is
        esetially a shortcut to pre-fill configuration data of a variant"""
        wizard_model = "product.configurator.sale"

        extra_vals = {
            "order_id": self.order_id.id,
            "order_line_id": self.id,
            "product_id": self.product_id.id,
        }
        self = self.with_context(
            {
                "default_order_id": self.order_id.id,
                "default_order_line_id": self.id,
            }
        )
        return self.product_id.product_tmpl_id.create_config_wizard(model_name=wizard_model, extra_vals=extra_vals
                                                                    )

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        if self.config_session_id:
            account_tax_obj = self.env["account.tax"]
            self.price_unit = account_tax_obj._fix_tax_included_price_company(
                self.config_session_id.price,
                self.product_id.taxes_id,
                self.tax_id,
                self.company_id,
            )
        else:
            super(SaleOrderLine, self).product_uom_change()


# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"

#     @api.model
#     def _prepare_from_pos(self, sale_order, order_line_data):
#         ProductProduct = self.env["product.product"]
#         product = ProductProduct.browse(order_line_data["product_id"])
#         return {
#             "order_id": sale_order.id,
#             "product_id": order_line_data["product_id"],
#             "name": product.name,
#             "product_uom_qty": order_line_data["qty"],
#             "discount": order_line_data["discount"],
#             "price_unit": order_line_data["price_unit"],
#             "tax_id": order_line_data["tax_ids"],
#         }

#     custom_value_ids = fields.One2many(comodel_name="product.config.session.custom.value", inverse_name="cfg_session_id", related="config_session_id.custom_value_ids", string="Configurator Custom Values",
#                                        )
#     config_ok = fields.Boolean(related="product_id.config_ok", string="Configurable", readonly=True
#                                )
#     config_session_id = fields.Many2one(comodel_name="product.config.session", string="Config Session"
#                                         )

#     def reconfigure_product(self):
#         """Creates and launches a product configurator wizard with a linked
#         template and variant in order to re-configure a existing product. It is
#         esetially a shortcut to pre-fill configuration data of a variant"""
#         wizard_model = "product.configurator.sale"

#         extra_vals = {
#             "order_id": self.order_id.id,
#             "order_line_id": self.id,
#             "product_id": self.product_id.id,
#         }
#         self = self.with_context(
#             {
#                 "default_order_id": self.order_id.id,
#                 "default_order_line_id": self.id,
#             }
#         )
#         return self.product_id.product_tmpl_id.create_config_wizard(model_name=wizard_model, extra_vals=extra_vals
#                                                                     )

#     @api.onchange("product_uom", "product_uom_qty")
#     def product_uom_change(self):
#         if self.config_session_id:
#             account_tax_obj = self.env["account.tax"]
#             self.price_unit = account_tax_obj._fix_tax_included_price_company(
#                 self.config_session_id.price,
#                 self.product_id.taxes_id,
#                 self.tax_id,
#                 self.company_id,
#             )
#         else:
#             super(SaleOrderLine, self).product_uom_change()
