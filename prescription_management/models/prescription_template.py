# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PrescriptionTemplate(models.Model):
    _name = "prescription.template"
    _description = "Draft Rx Template"

    active = fields.Boolean(
        default=True,
        help="If unchecked, it will allow you to hide the quotation template without removing it.")
    company_id = fields.Many2one(comodel_name='res.company')

    name = fields.Char(string="Draft Rx Template", required=True)
    note = fields.Html(string="Terms and conditions", translate=True)

    prescription_template_line_ids = fields.One2many(
        comodel_name='prescription.template.line', inverse_name='prescription_template_id',
        string="Lines",
        copy=True)
    prescription_template_option_ids = fields.One2many(
        comodel_name='prescription.template.option', inverse_name='prescription_template_id',
        string="Optional Products",
        copy=True)

    #=== CONSTRAINT METHODS ===#

    @api.constrains('company_id', 'prescription_template_line_ids', 'prescription_template_option_ids')
    def _check_company_id(self):
        for template in self:
            companies = template.mapped('prescription_template_line_ids.product_id.company_id') | template.mapped('prescription_template_option_ids.product_id.company_id')
            if len(companies) > 1:
                raise ValidationError(_("Your template cannot contain products from multiple companies."))
            elif companies and companies != template.company_id:
                raise ValidationError(_(
                    "Your template contains products from company %(product_company)s whereas your template belongs to company %(template_company)s. \n Please change the company of your template or remove the products from other companies.",
                    product_company=', '.join(companies.mapped('display_name')),
                    template_company=template.company_id.display_name,
                ))

    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._update_product_translations()
        return records

    def write(self, vals):
        if 'active' in vals and not vals.get('active'):
            companies = self.env['res.company'].sudo().search([('prescription_template_id', 'in', self.ids)])
            companies.prescription_template_id = None
        result = super().write(vals)
        self._update_product_translations()
        return result

    def _update_product_translations(self):
        languages = self.env['res.lang'].search([('active', '=', 'true')])
        for lang in languages:
            for line in self.prescription_template_line_ids:
                if line.name == line.product_id.get_product_multiline_description_sale():
                    line.with_context(lang=lang.code).name = line.product_id.with_context(lang=lang.code).get_product_multiline_description_sale()
            for option in self.prescription_template_option_ids:
                if option.name == option.product_id.get_product_multiline_description_sale():
                    option.with_context(lang=lang.code).name = option.product_id.with_context(lang=lang.code).get_product_multiline_description_sale()
