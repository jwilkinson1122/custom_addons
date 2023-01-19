from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = ["sale.order"]
    # _inherits = {
    #     'res.partner': 'partner_id',
    # }

    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Doctor')

    practice_id = fields.Many2one('res.partner', required=True, domain=[
        ('is_location', '=', True)], ondelete='restrict', copy=True)

    # practitioner_id = fields.Many2one('res.partner', required=True, domain=[
    #     ('is_practitioner', '=', True)], ondelete='restrict', copy=True)
    practitioner_id = fields.Many2one("podiatry.practitioner", 'Practitioner')

    patient_id = fields.Many2one('res.partner', required=True, domain=[
        ('is_patient', '=', True)], ondelete='restrict', copy=True)

    def action_config_start(self):
        """Return action to start configuration wizard"""
        configurator_obj = self.env["product.configurator.sale"]
        ctx = dict(
            self.env.context, default_order_id=self.id, wizard_model="product.configurator.sale", allow_preset_selection=True,
        )
        return configurator_obj.with_context(ctx).get_wizard_action()

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     for rec in self:
    #         return {'domain': {'practitioner_id': [('partner_id', '=', rec.partner_id.id)]}}

    # @api.onchange('practitioner_id')
    # def onchange_practitioner_id(self):
    #     for rec in self:
    #         return {'domain': {'patient_id': [('practitioner_id', '=', rec.practitioner_id.id)]}}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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
