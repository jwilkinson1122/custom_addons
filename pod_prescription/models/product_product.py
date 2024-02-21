

from datetime import time, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    default_code = fields.Char(index=True)
    attribute_value_ids = fields.Many2many('product.attribute.value', string='Attribute Values for Import')
    
    # prescription_ok = fields.Boolean(string="Can be Configured")
    is_helpdesk = fields.Boolean("Helpdesk Ticket?")
    helpdesk_team = fields.Many2one('helpdesk.team', string='Helpdesk Team')
    helpdesk_assigned_to = fields.Many2one('res.users', string='Assigned to')
    warranty_months = fields.Integer("Warranty (months)")
    prescription_count = fields.Float(compute='_compute_prescription_count', string='Sold', digits='Product Unit of Measure')

    # Catalog related fields
    product_catalog_product_is_in_prescription_order = fields.Boolean( 
        compute='_compute_product_is_in_prescription_order', 
        search='_search_product_is_in_prescription_order',
    )
    
    def get_product_multiline_description_prescription(self):
        """ Compute a multiline description of this product, in the context of prescription orders
                (do not use for purchases or other display reasons that don't intend to use "description_prescription").
            It will often be used as the default description of a prescription order line referencing this product.
        """
        name = self.display_name
        if self.description_prescription:
            name += '\n' + self.description_prescription

        return name

    def _compute_prescription_count(self):
        r = {}
        self.prescription_count = 0
        if not self.user_has_groups('pod_prescription_team.group_prescription_personnel'):
            return r
        date_from = fields.Datetime.to_string(fields.datetime.combine(fields.datetime.now() - timedelta(days=365),
                                                                      time.min))

        done_states = self.env['prescription.report']._get_done_states()

        domain = [
            ('state', 'in', done_states),
            ('product_id', 'in', self.ids),
            ('date', '>=', date_from),
        ]
        for product, product_uom_qty in self.env['prescription.report']._read_group(domain, ['product_id'], ['product_uom_qty:sum']):
            r[product.id] = product_uom_qty
        for product in self:
            if not product.id:
                product.prescription_count = 0.0
                continue
            product.prescription_count = float_round(r.get(product.id, 0), precision_rounding=product.uom_id.rounding)
        return r

    @api.onchange('type')
    def _onchange_type(self):
        if self._origin and self.prescription_count > 0:
            return {'warning': {
                'title': _("Warning"),
                'message': _("You cannot change the product's type because it is already used in prescription orders.")
            }}

    @api.depends_context('order_id')
    def _compute_product_is_in_prescription_order(self):
        order_id = self.env.context.get('order_id')
        if not order_id:
            self.product_catalog_product_is_in_prescription_order = False
            return

        read_group_data = self.env['prescription.order.line']._read_group( domain=[('order_id', '=', order_id)], groupby=['product_id'], aggregates=['__count'],
        )
        data = {product.id: count for product, count in read_group_data}
        for product in self:
            product.product_catalog_product_is_in_prescription_order = bool(data.get(product.id, 0))

    def _search_product_is_in_prescription_order(self, operator, value):
        if operator not in ['=', '!='] or not isinstance(value, bool):
            raise UserError(_("Operation not supported"))
        product_ids = self.env['prescription.order.line'].search([
            ('order_id', 'in', [self.env.context.get('order_id', '')]),
        ]).product_id.ids
        return [('id', 'in', product_ids)]

    def action_view_prescription(self):
        action = self.env["ir.actions.actions"]._for_xml_id("pod_prescription.report_all_channels_prescription_action")
        action['domain'] = [('product_id', 'in', self.ids)]
        action['context'] = {
            'pivot_measures': ['product_uom_qty'],
            'active_id': self._context.get('active_id'),
            'search_default_Prescription': 1,
            'active_model': 'prescription.report',
            'search_default_filter_order_date': 1,
        }
        return action

    def _get_invoice_policy(self):
        return self.invoice_policy

    def _filter_to_unlink(self):
        domain = [('product_id', 'in', self.ids)]
        lines = self.env['prescription.order.line']._read_group(domain, ['product_id'])
        linked_product_ids = [product.id for [product] in lines]
        return super(ProductProduct, self - self.browse(linked_product_ids))._filter_to_unlink()

    # 'https://www.youtube.com/watch?v=VyhwkhnwIck&list=PLSKcWRTtEl5qzvRaI-VTGavfReiHS_EEb&index=6'

    @api.depends('product_template_attribute_value_ids')
    def _compute_combination_indices(self):
        if self.env.context.get('import_ex_thread', False):
            return True
        super(ProductProduct,self)._compute_combination_indices()
    
    @api.model
    def make_variant_code_auto(self,new_obj):
        d_default_code = new_obj.product_tmpl_id.default_code
        if len(new_obj.product_variant_ids)>1:
            d_default_code = '%s-%s' % (d_default_code,new_obj.id)
        
        return d_default_code
    
    @api.model
    def process_after_save(self,vals,data_obj):
        if 'attribute_value_ids' in vals:
            ptal_pool = self.env['product.template.attribute.line'].sudo().with_context(update_product_template_attribute_values=False)
            ptav_pool = self.env['product.template.attribute.value'].sudo()
            tmp_line_obj = False
            tmp_lines = False
            tmp_ptav_ids = []
            tmp_value = data_obj.product_tmpl_id.id
            for child_val in data_obj.attribute_value_ids:
                tmp_lines = ptal_pool.search([('product_tmpl_id','=',tmp_value),
                                              ('attribute_id','=',child_val.attribute_id.id)], limit=1)
                if tmp_lines:
                    tmp_line_obj = tmp_lines[0]
                    if child_val.id not in tmp_line_obj.value_ids.ids:
                        tmp_line_obj.write({'value_ids':[(4,child_val.id)]})
                else:
                    tmp_line_obj = ptal_pool.create({'product_tmpl_id':tmp_value,
                                      'attribute_id':child_val.attribute_id.id,
                                      'value_ids':[(6,0,[child_val.id])]})
                
                
                tmp_lines = ptav_pool.search([('product_tmpl_id','=',tmp_value),
                                              ('attribute_line_id','=',tmp_line_obj.id),
                                              ('product_attribute_value_id','=',child_val.id)],limit=1)
                if tmp_lines:
                    tmp_ptav_ids.append(tmp_lines[0].id)
                else:
                    tmp_line_obj = ptav_pool.create({'product_tmpl_id': tmp_value,
                                      'attribute_line_id': tmp_line_obj.id,
                                      'product_attribute_value_id': child_val.id
                                      })
                    tmp_ptav_ids.append(tmp_line_obj.id)
            
            super(ProductProduct,data_obj).write({'product_template_attribute_value_ids':[(6,0,tmp_ptav_ids)]})
            data_obj.with_context(import_ex_thread=False)._compute_combination_indices()
    
    @api.model
    def create(self,vals):
        new_obj = super(ProductProduct,self.with_context(product_template_code=vals.get('default_code',False))).create(vals)
        self.process_after_save(vals=vals,data_obj=new_obj)
        if not new_obj.default_code:
            d_default_code = self.make_variant_code_auto(new_obj=new_obj)
            new_obj.write({'default_code':d_default_code})
        return new_obj
    
    def write(self, vals):
        for data in self:
            tmp_vals = vals.copy()
            super(ProductProduct, data).write(tmp_vals)
            self.process_after_save(vals=tmp_vals,data_obj=data)
        return True
    

class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    # prescription_order_line_id = fields.Many2one(
    #     "prescription.order.line",
    #     string="Prescription Order Line",
    #     required=True,
    #     ondelete="cascade",
    # )
    
    prescription_order_line_id = fields.Many2one(
        'prescription.order.line', 
        string="Prescription Order Line", 
        ondelete='cascade',
        relation='rx_order_line_attr_value_rel'  # Shorter table name
    )

    _sql_constraints = [
        ('rxl_custom_value_unique', 'unique(custom_product_template_attribute_value_id, prescription_order_line_id)', "Only one Custom Value is allowed per Attribute Value per Prescription Order Line.")
    ]

class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    prescription = fields.Boolean("Prescription", default=True, help="If true, the packaging can be used for prescription orders")
