# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    optometrist_id = fields.Many2one('hr.employee', required=True, domain=[('is_optometrist', '=', True)], ondelete='restrict', copy=True)
    prescription_note = fields.Text(string="Prescription Note", copy=True)

    right_sph = fields.Many2one('optical.sph.type', rel='sale_order_optical_sph_type_right', ondelete='restrict', copy=True)
    right_cyl = fields.Many2one('optical.cyl.type', rel='sale_order_optical_cyl_type_right', ondelete='restrict', copy=True)
    right_axis = fields.Many2one('optical.axis.type', rel='sale_order_optical_axis_type_right', ondelete='restrict', copy=True)
    right_prism = fields.Many2one('optical.prism.type', rel='sale_order_optical_prism_type_right', ondelete='restrict', copy=True)
    right_add = fields.Many2one('optical.add.type', rel='sale_order_optical_add_type_right', ondelete='restrict', copy=True)
    right_va = fields.Char(string="VA", copy=True)
    right_pd = fields.Char(string="PD", copy=True)

    left_sph = fields.Many2one('optical.sph.type', rel='sale_order_optical_sph_type_left', ondelete='restrict', copy=True)
    left_cyl = fields.Many2one('optical.cyl.type', rel='sale_order_optical_cyl_type_left', ondelete='restrict', copy=True)
    left_axis = fields.Many2one('optical.axis.type', rel='sale_order_optical_axis_type_left', ondelete='restrict', copy=True)
    left_prism = fields.Many2one('optical.prism.type', rel='sale_order_optical_prism_type_left', ondelete='restrict', copy=True)
    left_add = fields.Many2one('optical.add.type', rel='sale_order_optical_add_type_left', ondelete='restrict', copy=True)
    left_va = fields.Char(string="VA", copy=True)
    left_pd = fields.Char(string="PD", copy=True)

    def get_optical_prescription_template_id(self):
        self.ensure_one()
        report_name = 'report_optical_prescription'
        template_obj = self.env['report.custom.template']

        template = template_obj.sudo().get_template(report_name)

        if not template:
            template_obj.reset_template(report_name=report_name)
            template = template_obj.sudo().get_template(report_name)
        return template


class ReportCustomTemplate(models.Model):
    _inherit = 'report.custom.template'

    def get_report_list(self):
        res = super(ReportCustomTemplate, self).get_report_list()

        res["report_optical_prescription"] = {

            'name_display': 'Optical Prescription Template',
            'template': 'pink',
            'paperformat_id': self.env.ref("odoo_optical.paperformat_optical_prescription").id,
            'visible_watermark': True,
            'lines': [
                {'name': 'Header Section',
                 'name_technical': 'section_header',
                 'model_id': 'res.company',
                 'type': 'address',
                 'color': ' #daa6a6',
                 'preview_img': '1_top.png',
                 'address_field_ids': [
                     (0, 0, {'prefix': False, 'sequence': 10, 'field_id': 'street', }),
                     (0, 0, {'prefix': 'next_line', 'sequence': 20, 'field_id': 'street2', }),
                     (0, 0, {'prefix': 'next_line', 'sequence': 30, 'field_id': 'city', }),
                     (0, 0, {'prefix': 'comma', 'sequence': 40, 'field_id': 'state_id', 'field_display_field_id': 'name', }),
                     (0, 0, {'prefix': 'comma', 'sequence': 50, 'field_id': 'zip', }),
                     (0, 0, {'prefix': 'next_line', 'sequence': 60, 'field_id': 'country_id', 'field_display_field_id': 'name', }),
                 ],
                 },

                {'name': 'Patient Address',
                 'name_technical': 'section_partner_address',
                 'model_id': 'res.partner',
                 'type': 'address',
                 'color': ' #bfb781',
                 'preview_img': '2_left.png',
                 'address_field_ids': [
                     (0, 0, {'prefix': False, 'sequence': 10, 'field_id': 'street', }),
                     (0, 0, {'prefix': 'next_line', 'sequence': 20, 'field_id': 'street2', }),
                     (0, 0, {'prefix': 'next_line', 'sequence': 30, 'field_id': 'city', }),
                     (0, 0, {'prefix': 'comma', 'sequence': 40, 'field_id': 'state_id', 'field_display_field_id': 'name'}),
                     (0, 0, {'prefix': 'comma', 'sequence': 50, 'field_id': 'zip', }),
                     (0, 0, {'prefix': 'next_line', 'sequence': 60, 'field_id': 'country_id', 'field_display_field_id': 'name'}),
                 ],
                 },

                {'name': 'Other Fields',
                 'name_technical': 'section_other_fields',
                 'model_id': 'sale.order',
                 'type': 'fields',
                 'color': '#81bcbf',
                 'preview_img': '2_right.png',
                 'field_ids': [
                     (0, 0, {'sequence': 10, 'field_id': 'optometrist_id', 'label': 'Optometrist'}),
                     (0, 0, {'sequence': 20, 'field_id': 'client_order_ref', 'label': 'Your Reference'}),
                     (0, 0, {'sequence': 30, 'field_id': 'date_order', 'label': 'Quotation Date'}),
                     (0, 0, {'sequence': 40, 'field_id': 'validity_date', 'label': 'Expiration'}),
                     (0, 0, {'sequence': 50, 'field_id': 'user_id', 'label': 'Salesperson'}),
                 ],
                 },

                {'name': 'Lines Section',
                 'name_technical': 'section_lines',
                 'model_id': 'sale.order.line',
                 'type': 'lines',
                 'color': '#9095c7',
                 'preview_img': '3_lines.png',
                 'data_field_names': 'display_type',
                 'line_field_ids': [
                     (0, 0, {'sequence': 10, 'alignment': 'left', 'field_id': 'name', 'label': 'Description'}),
                     (0, 0, {'sequence': 20, 'alignment': 'center', 'field_id': 'product_uom_qty', 'label': 'Quantity'}),
                     (0, 0, {'sequence': 30, 'alignment': 'right', 'field_id': 'price_unit', 'label': 'Unit Price'}),
                     (0, 0, {'sequence': 40, 'alignment': 'center', 'field_id': 'product_uom', 'label': 'UOM'}),
                     (0, 0, {'sequence': 50, 'alignment': 'right', 'field_id': 'discount', 'label': 'Disc.%', 'null_hide_column': True}),
                     (0, 0, {'sequence': 60, 'alignment': 'center', 'field_id': 'tax_id', 'label': 'Taxes'}),
                     (0, 0, {'sequence': 70, 'alignment': 'right', 'field_id': 'price_subtotal', 'label': 'Amount', 'currency_field_name': 'order_id.currency_id', 'thousands_separator': 'applicable'}),
                 ],
                 },

                {'name': 'Bottom Amount Section',
                 'name_technical': 'section_bottom_amount',
                 'model_id': 'sale.order',
                 'type': 'fields',
                 'color': '#81bcbf',
                 'preview_img': '4_bottom_right.png',
                 'field_ids': [
                     (0, 0, {'sequence': 10, 'thousands_separator': 'applicable', 'field_id': 'amount_untaxed', 'label': 'Untaxed Amount'}),
                     (0, 0, {'sequence': 20, 'thousands_separator': 'applicable', 'field_id': 'amount_tax', 'label': 'Tax'}),
                     (0, 0, {'sequence': 30, 'thousands_separator': 'applicable', 'field_id': 'amount_total', 'label': 'Amount With Tax'}),
                 ],
                 },

                {'name': 'Footer Section',
                 'name_technical': 'section_footer',
                 'model_id': 'res.company',
                 'type': 'address',
                 'color': ' #dcaf95',
                 'preview_img': '5_bottom.png',
                 'address_field_ids': [
                     (0, 0, {'label': 'Phone', 'sequence': 10, 'field_id': 'phone' }),
                     (0, 0, {'label': 'Email', 'sequence': 20, 'field_id': 'email' }),
                     (0, 0, {'label': 'Web', 'sequence': 30, 'field_id': 'website' }),
                     (0, 0, {'label': 'Tax ID', 'sequence': 40, 'field_id': 'vat' }),
                 ],
                 },

                {'name': 'Other Options',
                 'name_technical': 'section_other_options',
                 'type': 'options',
                 'color': ' #93c193',
                 'preview_img': 'other.png',
                 'option_field_ids': [
                     (0, 0, {'field_type': 'char', 'name_technical': 'state_order', 'name': 'HEADING:IF STATE IS DRAFT/SENT', 'value_char': 'PRESCRIPTION'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'state_quotation', 'name': 'HEADING:IF STATE IS NOT DRAFT/SENT', 'value_char': 'PRESCRIPTION'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'heading_lens_details', 'name': 'HEADING:LENS DETAILS SECTION', 'value_char': 'PRESCRIPTION'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'heading_orderline_details', 'name': 'HEADING:ORDER LINE DETAILS', 'value_char': 'PRODUCTS / SERVICES'}),
                     (0, 0, {'field_type': 'combo_box', 'name_technical': 'header_section_sequence','key_combo_box': 'report_utils2__header_section_sequence', 'name': 'Order of Header Section', 'value_combo_box': 'address_logo_reference', }),
                     (0, 0, {'field_type': 'break', 'name_technical': '-1', 'name': '-',}),

                     (0, 0, {'field_type': 'char', 'name_technical': 'label_customer', 'name': 'LABEL: Patient', 'value_char': 'PATIENT'}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_shipping_address', 'name': 'Show shipping address', 'value_boolean': False}),
                     (0, 0, {'field_type': 'break', 'name_technical': '-1', 'name': '-',}),

                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_serial_number', 'name': 'Show serial number ?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'serial_number_heading', 'name': 'Serial number heading', 'value_char': 'Sl.'}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_product_image', 'name': 'Show product image ?', 'value_boolean': False}),
                     (0, 0, {'field_type': 'integer', 'name_technical': 'product_image_position', 'name': 'Product image position (Column)', 'value_integer': 2}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'product_image_column_heading', 'name': 'Product image heading', 'value_char': 'Product Image'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'product_image_width', 'name': 'Product image width', 'value_char': '75px'}),
                     (0, 0, {'field_type': 'break', 'name_technical': '-1', 'name': '-',}),

                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_amount_in_text', 'name': 'Show Amount in Words ?', 'value_boolean': False}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'label_amount_in_text', 'name': 'Label Amount in Words', 'value_char': 'Amount In Text'}),
                     (0, 0, {'field_type': 'break', 'name_technical': '-1', 'name': '-',}),

                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_note', 'name': 'Show Terms & Conditions ?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_payment_term_note', 'name': 'Show Payment Terms Remark ?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_fiscal_position_note', 'name': 'Show Fiscal Position Remark ?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_company_tagline_footer', 'name': 'Show Company tagline Footer ?', 'value_boolean': True}),

                 ],
                 },
            ],
        }

        return res


