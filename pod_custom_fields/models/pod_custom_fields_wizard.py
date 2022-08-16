# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.exceptions import UserError
import xml.etree.ElementTree as ET
import types
import re


class account_invoice(models.Model):
    _inherit = 'sale.order'

    dummy = fields.Char('Dummy')


class IrModelSelectionFieldInherit(models.Model):
    """docstring for IrModelFieldInherit"""

    _name = "ir.model.fields.selection.sale"
    _description = "Sale Fields Selection"

    fields_id = fields.Many2one('ir.models.fields.sale')
    field = fields.Many2one('ir.model.fields')
    value = fields.Char(string="Value")
    name = fields.Char(string="name")


class ir_model_fields(models.Model):

    _name = 'ir.models.fields.sale'
    _inherit = 'ir.model.fields'
    _description = "Sale Fields"

    def _get_fields_type(self):
        # Avoid too many nested `if`s below, as RedHat's Python 2.6
        # break on it. See bug 939653.
        res = [('binary', 'binary'), ('boolean', 'boolean'), ('char', 'char'), ('date', 'date'),
               ('datetime', 'datetime'), ('float',
                                          'float'), ('html', 'html'), ('integer', 'integer'),
               ('many2one', 'many2one'), ('selection', 'selection'), ('text', 'text')]

        return res

    name = fields.Char('Name', default='x_')
    model_id = fields.Many2one('ir.model', 'model', required=True,  ondelete='cascade',
                               help="The model this field belongs to")
    field_description = fields.Char('Description')
    help = fields.Char('Help')
    selection = fields.Char('Selection')
    ttype = fields.Char('Data Type')
    where_to_add = fields.Selection(
        [('after', 'After'), ('before', 'Before')], string="Where to Add", required=True)
    relation = fields.Char('Relation')
    state = fields.Char('State')
    relation_field = fields.Char('Relation Field')
    groups = fields.Many2many('res.groups', 'ir_models_fields_sale_group_rel', 'field_id',
                              'group_id')  # CLEANME unimplemented field (empty table)

    after_which_field_sale = fields.Many2one(
        'ir.model.fields', string="Field", ondelete="cascade", required=True)

    ttype = fields.Selection(_get_fields_type, 'Field Type', required=True, )
    selection_ids = fields.One2many("ir.model.fields.selection.sale", "fields_id",
                                    string="Selection Options", copy=True)

    @api.model
    def create(self, values):
        ir_model_obj = self.env['ir.model']
        model_id = ir_model_obj.search([('model', '=', 'sale.order')])
        values.update({'model_id': model_id.id, 'state': 'manual'})
        field_id = super(ir_model_fields, self).create(values)
        main_class_obj = self.env['ir.model.fields']
        model_id = ir_model_obj.search([('model', '=', 'sale.order')])
        if model_id:
            model_id = model_id[0]
        field = main_class_obj.create({'model_id': model_id.id,
                                       'name': values.get('name'),
                                       'state': values.get('state'),
                                       'ttype': values.get('ttype'),
                                       'model': values.get('res.partner'),
                                       'field_description': values.get('field_description'),
                                       'help': values.get('help'),
                                       'relation': values.get('relation'),
                                       'relation_field': values.get('relation_field'),
                                       })
        selection_model = self.env['ir.model.fields.selection']
        if not values.get('selection_ids') and values.get('ttype') == 'selection':
            raise UserError('Please Add values for selection')

        if values.get('selection_ids'):
            for rec in values.get('selection_ids'):
                rec[2].update({'field_id': field.id})
                selection_model.create(rec[2])

        return field_id

    @api.onchange('ttype')
    def filter_fields(self):

        model_name = 'sale.order'
        fields = []
        view_id = self.env['ir.ui.view'].sudo().search([('model', '=', model_name), (
            'type', '=', 'form'), ('active', '=', True), ('inherit_id', '=', False)], limit=1)

        if view_id:
            view_architecture = str(view_id.arch_base)
            document = ET.fromstring(view_architecture)
            for tag in document.findall('.//field'):
                if tag.attrib['name'] not in fields:
                    fields.append(tag.attrib['name'])
        return {'domain': {'after_which_field_sale': [('name', 'in', fields), ('model_id.model', '=', 'sale.order')]}}

    def custom_field_add(self):
        ir_ui_view_obj = self.env['ir.ui.view']
        # checking that ir.ui.view object is already created or not
        # if self._context.get('type') == 'out_invoice':
        #   search_inherited_view_id  = ir_ui_view_obj.search([('name','=','bi_inherit_customer_invoice_view')])
        # else:
        #  search_inherited_view_id  = ir_ui_view_obj.search([('name','=','bi_inherit_vendor_bill_view')])
        search_inherited_view_id = ir_ui_view_obj.search(
            [('name', '=', 'bi_inherit_sale_order_view')])
        if not search_inherited_view_id:
            MODULE = 'pod_custom_fields'
            '''
			if self._context.get('type') == 'out_invoice':
					name = 'bi_inherit_customer_invoice_view'
					inherit_id = 'account.invoice_form'
			else:
					name = 'bi_inherit_vendor_bill_view'
					inherit_id = 'account.invoice_supplier_form'
			'''
            arch = "<data><field name=" + '"' + self.after_which_field_sale.name + '"' + " " + "position=" + '"' + \
                self.where_to_add + '"' + ">" + "<field name=" + '"' + \
                self.name + '"' + "/>" + "</field>" + "</data>"
            registry = self.env
            type = 'form'
            view_id = registry['ir.model.data']._xmlid_to_res_id(
                "%s.%s" % (MODULE, name))
            if view_id:
                registry['ir.ui.view'].write([view_id], {
                    'arch': arch,
                })

            try:
                view_id = registry['ir.ui.view'].create({
                    'name': name,
                    'type': type,
                    'arch': arch,
                    'model': 'sale.order',
                    'inherit_id': registry['ir.model.data']._xmlid_to_res_id(inherit_id, raise_if_not_found=True)
                })
            except:
                import traceback
                traceback.print_exc()
                return
            registry['ir.model.data'].create({
                'name': name,
                'model': 'ir.ui.view',
                'module': MODULE,
                'res_id': view_id,
                'noupdate': False,
            })
            # reload parent view
            return {

                'view_id': view_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': self._context.get('active_id'),
                'type': 'ir.actions.act_window',
                'context': {'active_ids': self._context.get('active_ids')},
                'type': 'ir.actions.client',
                'tag': 'reload'

            }
        else:
            # getting view id and all details about cutome fields and there archs
            arch_data_start = "<data>"
            arch_end_data = "</data>"
            # all custom fields details in this
            search_id = self.search(
                [('state', '=', 'manual'), ('model_id', '=', 'sale.order')])
            middel_arch_data = ''
            for c_field_id in search_id:
                if c_field_id.after_which_field_sale.name == "date_order":
                    if c_field_id.where_to_add == "after":
                        middel_arch_data += '''<xpath expr="//field[@name='date_order'][2]" position="after">''' + \
                            "<field name=" + '"' + c_field_id.name + '"' + "/>" + "</xpath>"
                    else:
                        middel_arch_data += '''<xpath expr="//group[@name='order_details']//div[hasclass('o_td_label')][1]" position="before">''' + \
                            "<field name=" + '"' + c_field_id.name + '"' + "/>" + "</xpath>"

                elif c_field_id.after_which_field_sale.name == "pricelist_id":
                    if c_field_id.where_to_add == "after":
                        middel_arch_data += '''<xpath expr="//group[@name='order_details']//div[hasclass('o_row')]" position="after">''' + \
                            "<field name=" + '"' + c_field_id.name + '"' + "/>" + "</xpath>"
                    else:
                        middel_arch_data += '''<xpath expr="//label[@for='pricelist_id']" position="before">''' + \
                            "<field name=" + '"' + c_field_id.name + '"' + "/>" + "</xpath>"

                elif c_field_id.after_which_field_sale.name == "company_id":
                    middel_arch_data += '''<xpath expr="//page[@name='other_information']//field[@name='company_id']" ''' + \
                        ''' position="''' + c_field_id.where_to_add + '">' + \
                        "<field name=" + '"' + c_field_id.name + '"' + "/>" + "</xpath>"

                else:
                    middel_arch_data += "<field name=" + '"' + c_field_id.after_which_field_sale.name + '"' + " " + "position=" + \
                        '"' + c_field_id.where_to_add + '"' + ">" + "<field name=" + \
                        '"' + c_field_id.name + '"' + "/>" + "</field>"
            final_arch_data = arch_data_start + middel_arch_data + arch_end_data
            search_inherited_view_id.write({'arch': final_arch_data})
            return {

                'view_id': search_inherited_view_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': self._context.get('active_id'),
                'type': 'ir.actions.act_window',
                'context': {'active_ids': self._context.get('active_ids')},
                'type': 'ir.actions.client',
                'tag': 'reload'

            }
            return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
