from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class CPQPriceMatrix(models.Model):
    _name = "cpq.price.matrix"
    _description = "Generic CPQ Price Matrix"

    name = fields.Char(compute="_compute_name", store=True)
    product_tmpl_id = fields.Many2one("product.template", required=False)

    ptav_ids = fields.Many2many(
        "cpq.attribute.value",
        "cpq_price_matrix_ptav_rel",
        "matrix_id", "value_id",
        string="Attribute Values",
        help="List of attribute values that define this pricing rule"
    )
    price_extra = fields.Float(string="Price Extra", required=True)

    def default_get(self, fields):
        res = super().default_get(fields)
        if 'product_tmpl_id' in self.env.context:
            res['product_tmpl_id'] = self.env.context['product_tmpl_id']
        return res
    
    hash_key = fields.Char(compute="_compute_hash_key", store=True)

    @api.depends('ptav_ids')
    def _compute_hash_key(self):
        for rec in self:
            rec.hash_key = "-".join(str(id) for id in sorted(rec.ptav_ids.ids))

    @api.depends('ptav_ids')
    def _compute_name(self):
        for rec in self:
            rec.name = " / ".join(av.name for av in rec.ptav_ids)

    def compute_price_for_configuration(self, selected_value_ids, template_id=None):
        matrix = self.env['cpq.price.matrix'].match_matrix(selected_value_ids, template_id)
        return matrix.price_extra if matrix else 0.0

    def match_matrix(self, value_ids, template_id=None):
        domain = [('ptav_ids', 'subset_of', value_ids)]
        if template_id:
            domain.append(('product_tmpl_id', '=', template_id))
        return self.search(domain, limit=1)
    

class CPQPriceMatrixLine(models.TransientModel):
    _name = "cpq.price.matrix.line"
    _description = "Create Price Matrix Line"

    product_tmpl_id = fields.Many2one('product.template', required=True)
    attribute_value_ids = fields.Many2many('product.attribute.value', string="Attribute Values")
    price_extra = fields.Float("Extra Price", required=True)

    # def default_get(self, fields):
    #     res = super().default_get(fields)
    #     if 'product_tmpl_id' in self.env.context:
    #         res['product_tmpl_id'] = self.env.context['product_tmpl_id']
    #     return res
    
    # hash_key = fields.Char(compute="_compute_hash_key", store=True)

    # @api.depends('ptav_ids')
    # def _compute_hash_key(self):
    #     for rec in self:
    #         rec.hash_key = "-".join(str(id) for id in sorted(rec.ptav_ids.ids))

    @api.onchange("product_tmpl_id")
    def _onchange_product_tmpl_id(self):
        domain = [('id', 'in', self.product_tmpl_id.valid_product_template_attribute_line_ids.mapped('value_ids').ids)]
        return {'domain': {'attribute_value_ids': domain}}

    def action_create_matrix_line(self):
        if not self.attribute_value_ids:
            raise ValidationError("You must select at least one attribute value.")

        self.env["cpq.price.matrix"].create({
            "product_tmpl_id": self.product_tmpl_id.id,
            "ptav_ids": [(6, 0, self.attribute_value_ids.ids)],
            "price_extra": self.price_extra

        })
