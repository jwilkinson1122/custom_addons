# -*- coding: utf-8 -*-
import datetime
import pytz
import base64
import logging
_logger = logging.getLogger(__name__)
from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.mimetypes import guess_mimetype


class OptionSelectionWizard(models.TransientModel):
    _name = "option.selection.wizard"
    _description = "Custom Option Selection"

    # Fields Definition
    laterality = fields.Selection([
            ('lt_single', 'Left'),
            ('rt_single', 'Right'),
            ('bl_pair', 'Bilateral')
        ], string='Laterality', required=True, default='bl_pair', help="Select which side the product is for.")
    option_selections = fields.One2many('option.selection.entry', 'wizard_id', string="Option Selections")
    custom_option_id = fields.Many2one('product.custom.options', string="Custom Option")
    order_line_id = fields.Many2one('prescription.order.line', string="Order Line")
    prod_tmpl_id = fields.Many2one('product.template', related="order_line_id.product_id.product_tmpl_id", string='Product Template')
    input_type = fields.Selection(related="custom_option_id.input_type", string="Input Type", help="Input type for the custom option.")
    
    # Dynamic Input Fields
    text_input = fields.Char(string="Input (Text)")
    area_input = fields.Text(string="Input (Area)")
    date_input = fields.Date(string="Input (Date)")
    datetime_input = fields.Datetime(string="Input (Datetime)")
    time = fields.Float('Time in 24 hours format')
    radio_input = fields.Many2one("product.custom.options.value", string="Input (Radio)")
    dropdown_input = fields.Many2one("product.custom.options.value", string="Input (Dropdown)")
    multi_input = fields.Many2many("product.custom.options.value", string="Input (Multiple)")
    checkbox_input = fields.Many2many("product.custom.options.value", string="Input (Checkbox)")
    file_input = fields.Binary(string="Input (File)")
    price = fields.Float(string="Price", digits='Product Price')

    def _prepare_option_data(self):
        """Prepare data for creating/updating prescription.custom.options based on wizard input."""
        inputData = {
            'field': self.text_input,
            'area': self.area_input,
            'date': self.date_input,
            'time': str(datetime.timedelta(hours=self.time)),
            'date_time': str(self.datetime_input.astimezone(pytz.timezone(self.env.user.tz or 'UTC')).replace(tzinfo=None)),
            'radio': self.radio_input.name,
            'drop_down': self.dropdown_input.name,
            'multiple': ', '.join(self.multi_input.mapped('name')),
            'checkbox': ', '.join(self.checkbox_input.mapped('name')),
            'file': "File Input",
        }[self.input_type]

        price_adjustment = self.custom_option_id.price
        if self.input_type in ['radio', 'drop_down', 'multiple', 'checkbox']:
            price_adjustment = sum(self.multi_input.mapped('price')) if self.input_type in ['multiple', 'checkbox'] else self.radio_input.price if self.input_type == 'radio' else self.dropdown_input.price

        return {
            'input_data': inputData,
            'price': price_adjustment,
            'file_data': self.file_input,
            'laterality': self.laterality,
        }

    def add_option(self):
        """Add or update an option based on the wizard's input."""
        option_data = self._prepare_option_data()
        option_data['custom_option_id'] = self.custom_option_id.id
        option_data['order_line_id'] = self.order_line_id.id

        if self.laterality == 'bl_pair':
            option_data['price'] *= 2

        # Append laterality info to input data for display purposes
        option_data['input_data'] += f" (Side: {dict(self._fields['laterality'].selection).get(self.laterality, '')})"

        # Logic to either create a new option or update an existing one
        existing_option = self.order_line_id.prescription_options_ids.filtered(lambda r: r.custom_option_id == self.custom_option_id)
        if existing_option:
            existing_option.write(option_data)
        else:
            self.env['prescription.custom.options'].create(option_data)

        return {
            'type': 'ir.actions.act_window_close',
        }

    def finalize_selections(self):
        """Apply all selected options to the prescription order line."""
        if not self.order_line_id:
            return {'warning': {'title': "No Order Line", 'message': "No prescription order line found to apply options to."}}
        
        for selection in self.option_selections:
            # Since option data preparation and creation logic is now encapsulated,
            # this method can directly use that logic to apply selections.
            self.add_option()

        # Optionally, after applying all options, further logic can be added here if needed.

        # Closing the wizard or redirecting the user after applying selections.
        return {
            'type': 'ir.actions.act_window_close',
        }


# class OptionSelectionWizard(models.TransientModel):
#     _name = "option.selection.wizard"
#     _description = "Custom Option Selection"

#     laterality = fields.Selection([
#             ('lt_single', 'Left'),
#             ('rt_single', 'Right'),
#             ('bl_pair', 'Bilateral')
#         ], string='Laterality', required=True, default='bl_pair', help="Select which side the product is for.")

#     option_selections = fields.One2many(
#         'option.selection.entry', 'wizard_id', string="Option Selections"
#     )

#     def _get_input_type(self):
#         return [
#             ('field', 'Text Field'),
#             ('area', 'Text Area'),
#             ('date', 'Date'),
#             ('date_time', 'Date & Time'),
#             ('time', 'Time'),
#             ('radio', 'Radio Button'),
#             ('multiple', 'Multiple Select'),
#             ('checkbox', 'Checkbox'),
#             ('drop_down', 'Dropdown'),
#             ('file', 'File'),
#         ]

#     custom_option_id = fields.Many2one('product.custom.options', string="Custom Option")
#     order_line_id = fields.Many2one('prescription.order.line', string="Order Line")
#     prod_tmpl_id = fields.Many2one('product.template',related="order_line_id.product_id.product_tmpl_id", string='Product Template')
#     input_type = fields.Selection(_get_input_type, related="custom_option_id.input_type", string="Input Type", help="Input type for the custom option.")

#     text_input = fields.Char(string="Input (Text)")
#     area_input = fields.Text(string="Input (Area)")
#     date_input = fields.Date(string="Input (Date)")
#     datetime_input = fields.Datetime(string="Input (Datetime)")
#     time = fields.Float('Time in 24 hours format')
#     radio_input = fields.Many2one("product.custom.options.value", string="Input (Radio)")
#     dropdown_input = fields.Many2one("product.custom.options.value", string="Input (Dropdown)")
#     multi_input = fields.Many2many("product.custom.options.value", string="Input (Multiple)")
#     checkbox_input = fields.Many2many("product.custom.options.value", string="Input (Checkbox)", relation='option_value_join')
#     file_input = fields.Binary(string="Input (File)")

#     price = fields.Float(string="Price", digits=dp.get_precision('Product Price'),
#         help="Price for the custom option.")

#     def add_option(self):
#         optionObj = self.custom_option_id
#         optionType = self.input_type
#         price = 0.00
#         inputData = ''
#         laterality = self.laterality or 'bl_pair'  
#         if optionType == 'field':
#             inputData = str(self.text_input)
#             price = optionObj.price
#         elif optionType == 'area':
#             inputData = str(self.area_input)
#             price = optionObj.price
#         elif optionType == 'date':
#             inputData = str(self.date_input)
#             price = optionObj.price
#         elif optionType == 'time':
#             inputData =str(datetime.timedelta(hours=self.time))
#             price = optionObj.price
#         elif optionType == 'date_time':
#             user_tz = self.env.user.tz or self.env.context.get('tz')                
#             user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc            
#             now_dt = self.datetime_input.astimezone(user_pytz).replace(tzinfo=None) 
#             inputData = str(now_dt)                                                 
#             price = optionObj.price
#         elif optionType == 'radio':
#             inputData = self.radio_input.name
#             price = self.radio_input.price
#         elif optionType == 'drop_down':
#             inputData = self.dropdown_input.name
#             price = self.dropdown_input.price
#         elif optionType == 'multiple':
#             inputData = ', '.join(self.multi_input.mapped('name'))
#             price = sum(self.multi_input.mapped('price'))
#         elif optionType == 'checkbox':
#             inputData = ', '.join(self.checkbox_input.mapped('name'))
#             price = sum(self.checkbox_input.mapped('price'))
#         elif optionType == 'file':
#             inputData = "File Input"
#             price = optionObj.price

#         description_ids = self.order_line_id.prescription_options_ids.filtered(
#             lambda r: r.custom_option_id == optionObj)
#         if laterality == 'bl_pair':
#             price *= 2 
        
#         laterality_data = f" (Side: {laterality.capitalize()})"
#         inputData += laterality_data

#         if description_ids:
#             description_id = description_ids[0]
#             description_id.update({
#                 'input_data': inputData,
#                 'file_data': self.file_input,
#                 'price': price,
#                 'laterality': laterality
#             })
#         else:
#             selection = self.order_line_id.option_selections.new({
#             'custom_option_id': optionObj.id,
#             'input_data': inputData,
#             'price': price,
#             'file_data': self.file_input,
#             'laterality': laterality,
#             })
#             self.order_line_id.option_selections += selection

#         return {
#             'name': ("Information"),
#             'view_mode': 'form',
#             'view_type': 'form',
#             'res_model': 'prescription.order.line',
#             'view_id': self.env.ref('pod_product_custom_options.prescription_order_line_custom_options_form').id,
#             'res_id': self.order_line_id.id,
#             'type': 'ir.actions.act_window',
#             'nodestroy': True,
#             'target': 'new',
#             'domain': '[]',
#         }

#     def finalize_selections(self):
#         order_line = self.order_line_id
#         if not order_line:
#             return {'warning': {'title': "No Order Line", 'message': "No prescription order line found to apply options to."}}
#         for selection in self.option_selections:
#             optionObj = self.custom_option_id
#             optionType = self.input_type
#             inputData = selection.input_data
#             price = selection.price
#             laterality = selection.laterality
#             if optionType == 'field':
#                 inputData = str(self.text_input)
#                 price = optionObj.price
#             elif optionType == 'area':
#                 inputData = str(self.area_input)
#                 price = optionObj.price
#             elif optionType == 'date':
#                 inputData = str(self.date_input)
#                 price = optionObj.price
#             elif optionType == 'time':
#                 inputData =str(datetime.timedelta(hours=self.time))
#                 price = optionObj.price
#             elif optionType == 'date_time':
#                 user_tz = self.env.user.tz or self.env.context.get('tz')                
#                 user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc            
#                 now_dt = self.datetime_input.astimezone(user_pytz).replace(tzinfo=None) 
#                 inputData = str(now_dt)                                                 
#                 price = optionObj.price
#             elif optionType == 'radio':
#                 inputData = self.radio_input.name
#                 price = self.radio_input.price
#             elif optionType == 'drop_down':
#                 inputData = self.dropdown_input.name
#                 price = self.dropdown_input.price
#             elif optionType == 'multiple':
#                 inputData = ', '.join(self.multi_input.mapped('name'))
#                 price = sum(self.multi_input.mapped('price'))
#             elif optionType == 'checkbox':
#                 inputData = ', '.join(self.checkbox_input.mapped('name'))
#                 price = sum(self.checkbox_input.mapped('price'))
#             elif optionType == 'file':
#                 inputData = "File Input"
#                 price = optionObj.price
            
#             new_custom_option = self.env['prescription.custom.options'].create({
#                 'custom_option_id': selection.custom_option_id.id,
#                 'order_line_id': order_line.id,
#                 'input_data': inputData,
#                 'price': price,
#                 'file_data': self.file_input,
#                 'laterality': laterality,
#             })

#             order_line.update_description_with_options(new_custom_option)
#             order_line.calculate_total_price()
#             self.option_selections.unlink()
            
#             return {'type': 'ir.actions.act_window_close'}

#     def cancel_action(self):
#         return {
#             'name': ("Information"),
#             'view_mode': 'form',
#             'view_type': 'form',
#             'res_model': 'prescription.order.line',
#             'view_id': self.env.ref('pod_product_custom_options.prescription_order_line_custom_options_form').id,
#             'res_id': self.order_line_id.id,
#             'type': 'ir.actions.act_window',
#             'nodestroy': True,
#             'target': 'new',
#             'domain': '[]',
#         }


class OptionSelectionEntry(models.TransientModel):
    _name = "option.selection.entry"
    _description = "Option Selection Entry"

    wizard_id = fields.Many2one('option.selection.wizard', string="Wizard")
    custom_option_id = fields.Many2one('product.custom.options', string="Custom Option")
    price = fields.Float(string="Price", digits=dp.get_precision('Product Price'),
        help="Price for the custom option value.")
    input_data = fields.Text(string="Input")
    file_data = fields.Binary(string="File Uploaded")
    laterality = fields.Selection([
            ('lt_single', 'Left'),
            ('rt_single', 'Right'),
            ('bl_pair', 'Bilateral')
        ], string='Laterality', required=True, default='bl_pair', help="Select which side the product is for.")
    

