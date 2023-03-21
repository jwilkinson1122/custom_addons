# -*- coding: utf-8 -*-
import ast
from odoo import models, fields, api

SEPARATORS = [
    ('next_line', 'Next Line'),
    ('comma', 'Comma'),
]

ALIGNMENT_VALS = [
    ('left', 'Left'),
    ('center', 'Center'),
    ('right', 'Right'),
]

DATE_FORMATS = [
    ("01_%d %b %Y", "18 Feb 2020"),
    ("02_%d/%b/%Y", "18/Feb/2020"),
    ("03_%d %B %Y", "18 February 2020"),
    ("04_%d/%m/%Y", "18/02/2020"),
    ("05_%d/%m/%y", "18/02/20"),
    ("06_%m/%d/%Y", "02/18/2020"),
    ("07_%d-%b-%Y", "18-Feb-2020"),
    ("08_%d. %b. %Y", "18.Feb. 2020"),
    ("09_%b %d, %y", "Feb 18, 20"),
    ("10_%B %d, %y", "February 18, 20"),
    ("11_%b %d, %Y", "Feb 18, 2020"),
    ("12_%B %d, %Y", "February 18, 2020"),
    ("13_%A, %d %b %Y", "Tuesday, 18 Feb 2020"),
    ("14_%A, %B %d, %Y", "Tuesday, February 18, 2020"),
    ("15_%a, %B %d, %Y", "Tue, February 18, 2020"),
    ("16_%a, %B %d, %y", "Tue, February 18, 20"),
    ("17_%a, %b %d, %Y", "Tue, Feb 18, 2020"),
    ("18_%a, %b %d, %y", "Tue, Feb 18, 20"),
]


def float_range(start, stop, step=1.0):
    result = []
    count = start
    while count <= stop:
        result.append(round(count, 2))
        count += step
    return result


# class ColorObject:
#
#     color1 = False
#     color2 = False
#     color3 = False
#
#     def __init__(self, a=None, b=None, c=None):
#         self.color1 = a
#         self.color2 = b
#         self.color3 = c


class Font:
    size = False
    family = False
    line_height = False

    def __init__(self, size="16px"):
        self.size = size
        self.family = "none"
        self.line_height = "normal"

    @staticmethod
    def convert_size_to_int(size):
        result = ast.literal_eval(size.replace("px", ""))
        return int(result)

    @staticmethod
    def convert_int_to_size(num):
        return str(num) + "px"

    def get_size(self, percent=None):
        size_int = self.convert_size_to_int(self.size)

        if percent:
            result = size_int * percent / 100
            return self.convert_int_to_size(round(result))


def getattr_new(obj, attribute):
    o = obj
    for each in attribute.split('.'):
        o = getattr(o, each)
    return o


def add_thousands_separator(num):
    if type(num) == int:
        return '{:,}'.format(num)
    return '{:,.2f}'.format(num)


def remove_decimal_zeros_from_number(num):
    decimal = num - int(num)
    if not decimal:
        return int(num)
    return num


def rchop(s, suffix):
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s


def get_all_font_list(with_extension=False):
    vals = []
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.dirname(dir_path) + '/static/fonts'
    for each in os.listdir(dir_path):
        if each.endswith('ttf'):
            font = each
            if not with_extension:
                font = rchop(font, ".ttf")
            vals.append((font, font))
    return sorted(vals)


FONT_LIST = get_all_font_list()


class ReportTemplate(models.Model):
    _name = 'report.custom.template'
    _rec_name = 'name_display'

    name = fields.Char(required=True, string='Technical Name')
    name_display = fields.Char(required=True, string='Report Name')
#     model_id = fields.Many2one('ir.model')
#     section_2_model_id = fields.Many2one('ir.model')
#     line_model_id = fields.Many2one('ir.model')
    multi_company_applicable = fields.Boolean(default=False)
    company_id = fields.Many2one("res.company")
    template_id = fields.Many2one('report.custom.template.template')
    template_preview = fields.Binary(related='template_id.image', readonly=True)
#     header_company_field_ids = fields.One2many('reporting.custom.template.header.field', 'report_id')
#     footer_company_field_ids = fields.One2many('reporting.custom.template.footer.field', 'report_id')
#     visible_partner_section = fields.Boolean(default=False)
#     partner_field_ids = fields.One2many('reporting.custom.template.partner.field', 'report_id')
#     visible_section_2 = fields.Boolean(default=False)
#     section_2_field_ids = fields.One2many('reporting.custom.template.section.2', 'report_id')
#     visible_section_lines = fields.Boolean(default=False)
#     section_lines_field_ids = fields.One2many('reporting.custom.template.section.line', 'report_id')
#     visible_section_footer = fields.Boolean(default=False)
#     section_footer_field_ids = fields.One2many('reporting.custom.template.section.footer', 'report_id')
    visible_watermark = fields.Boolean()
    watermark = fields.Binary()
    watermark_opacity = fields.Selection([("%.2f" % x, "%.2f" % x) for x in float_range(start=0.12, stop=0.88, step=0.04)], string="Watermark Opacity")
    watermark_size = fields.Selection([('220px', 'Small'), ('400px', 'Medium'), ('600px', 'Large')], default='400px')
#     amount_in_text_visible = fields.Boolean(default=False)
#     amount_in_text_applicable = fields.Boolean(string="Amount In Text")
#     amount_in_text_label = fields.Char(string="Label")
#     section_other_option_ids = fields.One2many("reporting.custom.template.section.option", "report_id")
    font_size = fields.Selection([(str(x), str(x)) for x in range(10, 29)], string="Font Size")
    font_family = fields.Selection(FONT_LIST, string="Font Family")
    font_line_height = fields.Selection([("%.1f" % x, "%.1f" % x) for x in float_range(start=0.8, stop=2.0, step=0.1)], string="Line Height")
    date_format = fields.Selection(DATE_FORMATS)
    show_header = fields.Boolean("Show Header ?")
    show_footer = fields.Boolean("Show Footer ?")
    paperformat_id = fields.Many2one('report.paperformat', 'Paper Format', ondelete="restrict")
#     visible_reset = fields.Boolean(default=False)
#     visible_signature_boxes = fields.Boolean(default=False)
#     signature_box_ids = fields.One2many('reporting.custom.template.sign.box', 'report_id')
    page_number_type = fields.Selection([
        ('none', 'No Page Number'),
        ('page:1/n', 'Page: 1 / 10'),
    ], string="Page No Type")
    line_ids = fields.One2many('report.custom.template.line', 'report_id')

    def reset_defaults(self):
        self.ensure_one()
        defaults = {
            'font_size': "16",
            'font_family': False,
            'page_number_type': 'page:1/n',
            'date_format': DATE_FORMATS[0][0],
            'show_header': True,
            'show_footer': True,
            'font_line_height': '1.4',
            'visible_watermark': False,
            'watermark': False,
            'watermark_opacity': False,
            'watermark_size': '400px',
        }
        self.write(defaults)

#     def update_create_fields_data(self, data, model):
#         for each in data:
#             field = each[2]['field_id']
#
#             if type(field) == str:
#                 model_id = self.env["ir.model"].search([('model', '=', model)])
#                 if not model_id:
#                     raise UserWarning("Can\'t find model:%s" % model)
#
#                 field_id = model_id.field_id.filtered(lambda x: x.name == field)
#                 if not field_id:
#                     raise UserWarning("Can\'t find field:%s-%s" % (model, field))
#
#                 each[2]['field_id'] = field_id.id

    def reset_template(self, report_name=None, company_id=None):
        if not company_id:
            company_id = self.company_id

        # Avoid Context From Button
        if type(report_name) == dict:
            report_name = report_name['report_name']

        report_name = report_name or self._context['report_name']

        report_list = self.get_report_list()

        data = report_list[report_name]

        template_id = self.env['report.custom.template.template'].search([
            ('name_technical', '=', data['template']),
            ('report_name', '=', report_name),
        ])

        for line in data['lines']:
            if line.get('model_id'):
                line['model_id'] = self.env["ir.model"].search([("model", "=", line['model_id'])]).id

            if line.get('address_field_ids'):
                for x in line.get('address_field_ids'):
                    field_id = self.env["ir.model.fields"].search([('name', '=', x[2]['field_id']), ('model_id', '=', line['model_id']),])
                    x[2]['field_id'] = field_id.id
                    if x[2].get('field_display_field_id'):
                        display_field_id = self.env["ir.model.fields"].search([('name', '=', x[2]['field_display_field_id']), ('model_id', '=', self.env["ir.model"].search([('model', '=', field_id.relation)]).id),])
                        x[2]['field_display_field_id'] = display_field_id.id
           
            if line.get('field_ids'):
                for x in line.get('field_ids'):
                    field_id = self.env["ir.model.fields"].search([('name', '=', x[2]['field_id']), ('model_id', '=', line['model_id']),])
                    x[2]['field_id'] = field_id.id
                    if x[2].get('field_display_field_id'):
                        display_field_id = self.env["ir.model.fields"].search([('name', '=', x[2]['field_display_field_id']), ('model_id', '=', self.env["ir.model"].search([('model', '=', field_id.relation)]).id),])
                        x[2]['field_display_field_id'] = display_field_id.id

            if line.get('line_field_ids'):
                for x in line.get('line_field_ids'):
                    field_id = self.env["ir.model.fields"].search([('name', '=', x[2]['field_id']), ('model_id', '=', line['model_id']),])
                    x[2]['field_id'] = field_id.id
                    if x[2].get('field_display_field_id'):
                        display_field_id = self.env["ir.model.fields"].search([('name', '=', x[2]['field_display_field_id']), ('model_id', '=', self.env["ir.model"].search([('model', '=', field_id.relation)]).id),])
                        x[2]['field_display_field_id'] = display_field_id.id

            if line.get('option_field_ids'):
                for x in line.get('option_field_ids'):
                    if x[2]['field_type'] == "combo_box":
                        combo_box = self.env['report.custom.template.options.combo.box.item'].search([('name_technical', '=', x[2]['value_combo_box']), ('key', '=', x[2].get('key_combo_box') or x[2]['name_technical']),])
                        x[2]['value_combo_box'] = combo_box.id

        vals = {
                'name': report_name,
                'name_display': data['name_display'],
                'multi_company_applicable': data.get('multi_company_applicable'),
                'company_id': company_id and company_id.id,
                'template_id': template_id.id,
                'visible_watermark': data.get('visible_watermark'),
                'paperformat_id': data.get('paperformat_id') or False,
                'line_ids': [(0, 0, x) for x in data['lines']],
        #         'model_id': self.env["ir.model"].search([("model", "=", data['model'])]).id,
        #         'visible_reset': data.get("visible_reset") or False,
        #         'visible_watermark': data.get('visible_watermark') or False,
        #         'visible_signature_boxes': data.get('visible_signature_boxes') or False,
        #         'signature_box_ids': data.get('signature_box_ids') or False,
        }

#         if data.get('section_2_model_id'):
#             vals['section_2_model_id'] = self.env["ir.model"].search([("model", "=", data['section_2_model_id'])]).id
#
#         if data.get('header_company_field_ids'):
#             self.update_create_fields_data(data['header_company_field_ids'], model="res.company")
#             vals['header_company_field_ids'] = data['header_company_field_ids']
#
#         if data.get('footer_company_field_ids'):
#             self.update_create_fields_data(data['footer_company_field_ids'], model="res.company")
#             vals['footer_company_field_ids'] = data['footer_company_field_ids']
#
#         if data.get('section_other_option_ids'):
#             vals['section_other_option_ids'] = data['section_other_option_ids']
#
#         vals['visible_section_2'] = data.get('visible_section_2')
#         if data.get('section_2_field_ids') and data.get('visible_section_2'):
#             vals['section_2_field_ids'] = data['section_2_field_ids']
#

        # report_id = self.search([('name', '=', report_name)])
        report_id = self.get_template(report_name, company_id=company_id)

        if report_id:
            report_id.line_ids = False
            report_id.reset_defaults()
            report_id.write(vals)
        else:
            report_id = self.create(vals)
            report_id.reset_defaults()

    def console_template(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'report.custom.template.console',
            'target': 'new',
            'view_mode': 'form',
            'context': {'report_id': self.id}
        }

    def get_template(self, name, company_id=None):

        domain = [
            ('name', '=', name.strip()),
            ('template_id', '!=', False),
        ]
        if company_id:
            domain.append(('company_id', '=', company_id.id))
        return self.search(domain, limit=1)

    def get_watermark_style(self):
        self.ensure_one()
        opacity = self.watermark_opacity or "0.22"
        size = self.watermark_size or "400px"
        left = {"220px": "38%", "400px": "29%", "600px": "18%"}.get(size, "29%")

        style = "position:absolute;left:{left};width:{size};height:auto;padding-top:40px;opacity:{opacity};".format(
            opacity=opacity,
            size=size,
            left=left,
        )
        return style

    def get_field_data(self, obj, field_id, display_field=None, currency_field_name=None, thousands_separator=None, remove_decimal_zeros=None):
        self.ensure_one()

        if not field_id:
            raise UserWarning('FieldNotFound')

        value = getattr(obj, field_id.name)
        if field_id.ttype == 'char':
            return value or ""
        elif field_id.ttype == 'many2one':
            if not value:
                return ""

            result = value.display_name
            if display_field:
                result = getattr(value, display_field)
            return result
            # return display_field and getattr(value, display_field) or value.display_name

        elif field_id.ttype == 'date':
            if not value:
                return ""
            date_format = self.date_format or DATE_FORMATS[0][0]
            return value.strftime(date_format.split('_')[1]) or ""

        elif field_id.ttype == 'datetime':
            if not value:
                return ""
            date_format = self.date_format or DATE_FORMATS[0][0]
            d = value.strftime(date_format.split('_')[1]) or ""
            t = value.strftime("%H:%M:%S") or ""
            return "%s %s" % (d, t)

        elif field_id.ttype in ['float', 'integer']:
            if remove_decimal_zeros:
                value = remove_decimal_zeros_from_number(value)

            if thousands_separator and thousands_separator == 'applicable':
                value = add_thousands_separator(value)

            return value

        elif field_id.ttype == 'many2many':
            value = ', '.join(map(lambda x: (display_field and getattr(x, display_field) or x.display_name), value))
            return value
        elif field_id.ttype == 'monetary':
            if remove_decimal_zeros:
                value = remove_decimal_zeros_from_number(value)

            if thousands_separator and thousands_separator == 'applicable':
                value = add_thousands_separator(value)

            with_currency = str(value)

            curr_field = currency_field_name or 'currency_id'
            currency_id = getattr_new(obj, curr_field)
            if currency_id:
                if currency_id.position == 'before':
                    with_currency = currency_id.symbol + ' ' + with_currency
                else:
                    with_currency = with_currency + ' ' + currency_id.symbol
            return with_currency
        return value and str(value)
#
#     def get_address_data(self, obj, o2m_field_id_name):
    def get_address_data(self, obj, name_technical):
        self.ensure_one()

        line_id = self.line_ids.filtered(lambda x: x.name_technical == name_technical)

        vals = []
        for line in line_id.address_field_ids.sorted(key=lambda r: r.sequence):
            if not line.field_id:
                continue

            value = self.get_field_data(obj=obj, field_id=line.field_id, display_field=line.field_display_field_id.name)

            prefix = ""
            if hasattr(line, 'prefix'):
                prefix = line.prefix
            separator = {'next_line': '<br/>', 'comma': ','}.get(prefix, "")

            vals.append({
                'label': line.label and line.label.strip(),
                'value': value,
                'separator': separator,
            })
        return vals
#
#     def get_o2m_data(self, obj, o2m_field_id_name, label_auto=True):
#         self.ensure_one()
#
#         vals = []
#         for line in getattr(self, o2m_field_id_name).sorted(key=lambda r: r.sequence):
#             if not line.field_id:
#                 continue
#
#             thousands_separator = hasattr(line, 'thousands_separator') and line.thousands_separator or False
#             value = self.get_field_data(obj=obj, field_id=line.field_id, display_field=line.field_display_field_id.name, thousands_separator=thousands_separator)
#
#             label = line.label and line.label.strip() or ""
#             if not label and label_auto:
#                 label = line.field_id.field_description
#
#             vals.append({
#                 'label': label,
#                 'value': value,
#                 'null_value_display': hasattr(line, 'null_value_display') and line.null_value_display or False
#             })
#         return vals

    def get_fields_ids_data(self, obj, name_technical, label_auto=True):
        self.ensure_one()

        line_id = self.line_ids.filtered(lambda x: x.name_technical == name_technical)

        vals = []
        for line in line_id.field_ids.sorted(key=lambda r: r.sequence):
            if not line.field_id:
                continue

            thousands_separator = hasattr(line, 'thousands_separator') and line.thousands_separator or False

            value = self.get_field_data(obj=obj, field_id=line.field_id, display_field=line.field_display_field_id.name, thousands_separator=thousands_separator)

            label = line.label and line.label.strip() or ""
            if not label and label_auto:
                label = line.field_id.field_description

            vals.append({
                'label': label,
                'value': value,
                'null_value_display': hasattr(line, 'null_value_display') and line.null_value_display or False
            })
        return vals

    def get_line_ids_data(self, obj, line_field_name, name_technical):
        self.ensure_one()
        line_id = self.line_ids.filtered(lambda x: x.name_technical == name_technical)

        data = []
        # Header
        vals = []
        for line in line_id.line_field_ids.sorted(key=lambda r: r.sequence):
            if not line.field_id:
                continue
            
            vals.append({
                'type': 'header',
                'field_name': line.field_id.name,
                'label': line.label and line.label.strip() or line.field_id.field_description,
                'value': False,
                'null_hide_column': line.null_hide_column,
                'invisible': False,
                'width_style': 'width:%s' % (line.width or 'auto'),
            })

        data.append(vals)

#         # Content
        for each in getattr(obj, line_field_name):
            vals = []
            for line in line_id.line_field_ids.sorted(key=lambda r: r.sequence):
                if not line.field_id:
                    continue

                value = self.get_field_data(obj=each, field_id=line.field_id, display_field=line.field_display_field_id.name, currency_field_name=line.currency_field_name, thousands_separator=line.thousands_separator, remove_decimal_zeros=line.remove_decimal_zeros)

                line_vals = {
                    'type': 'content',
                    'field_name': line.field_id.name,
                    'label': line.label and line.label.strip() or line.field_id.field_description,
                    'value': value,
                    'null_hide_column': line.null_hide_column,
                    'invisible': False,
                    'alignment_style': 'text-align:%s' % (line.alignment or 'left'),
                    'line_id': each,
                }

                # Additional Fields
                if line_id.data_field_names:
                    for data_field_name in line_id.data_field_names.split(','):
                        if not data_field_name.strip():
                            continue

                        field_id = self.env["ir.model.fields"].search([('name', '=', data_field_name), ('model_id', '=', line_id.model_id.id),])
                        if not field_id:
                            raise UserWarning("Field Not Found: %s (%s)" % (data_field_name, line_id.model_id.model))

                        value2 = self.get_field_data(obj=each, field_id=field_id)

                        line_vals[data_field_name] = value2

                vals.append(line_vals)
            data.append(vals)

        # null_hide_column
        field_data = {}
        for row in data:
            for col in row:
                if col['null_hide_column']:
                    field_name = col['field_name']
                    value = col['value']
                    if field_name in field_data:
                        field_data[field_name].append(value)
                    else:
                        field_data[field_name] = [value]

        for row in data:
            for col in row:
                if col['null_hide_column']:
                    val_list = field_data.get(col['field_name']) or []
                    if not any(val_list):
                        col['invisible'] = True

        return data

#     def get_o2m_data_lines_section(self, obj, line_field_name, o2m_field_id_name):
#         self.ensure_one()
#
#         data = []
#         # Header
#         vals = []
#         for line in getattr(self, o2m_field_id_name).sorted(key=lambda r: r.sequence):
#             if not line.field_id:
#                 continue
#
#             vals.append({
#                 'type': 'header',
#                 'field_name': line.field_id.name,
#                 'label': line.label and line.label.strip() or line.field_id.field_description,
#                 'value': False,
#                 'null_hide_column': line.null_hide_column,
#                 'invisible': False,
#                 'width_style': 'width:%s' % (line.width or 'auto'),
#             })
#         data.append(vals)
#
#         # Content
#         for each in getattr(obj, line_field_name):
#             vals = []
#             for line in getattr(self, o2m_field_id_name).sorted(key=lambda r: r.sequence):
#                 if not line.field_id:
#                     continue
#
#                 value = self.get_field_data(obj=each, field_id=line.field_id, display_field=line.field_display_field_id.name, currency_field_name=line.currency_field_name, thousands_separator=line.thousands_separator)
#                 vals.append({
#                     'type': 'content',
#                     'field_name': line.field_id.name,
#                     'label': line.label and line.label.strip() or line.field_id.field_description,
#                     'value': value,
#                     'null_hide_column': line.null_hide_column,
#                     'invisible': False,
#                     'alignment_style': 'text-align:%s' % (line.alignment or 'left'),
#                     'line_id': each,
#                 })
#             data.append(vals)
#
#         # null_hide_column
#         field_data = {}
#         for row in data:
#             for col in row:
#                 if col['null_hide_column']:
#                     field_name = col['field_name']
#                     value = col['value']
#                     if field_name in field_data:
#                         field_data[field_name].append(value)
#                     else:
#                         field_data[field_name] = [value]
#
#         for row in data:
#             for col in row:
#                 if col['null_hide_column']:
#                     val_list = field_data.get(col['field_name']) or []
#                     if not any(val_list):
#                         col['invisible'] = True
#         return data
#
    def get_parameters(self):
        self.ensure_one()

        class ParametersObject:
            pass
        parameters = ParametersObject()
        if not self.template_id:
            raise UserWarning("Couldn\'t find template.")
        for key, value in self.template_id.parameter_values().items():
            setattr(parameters, key, value)
        return parameters

    def get_font(self):
        self.ensure_one()
        font = Font()

        font.size = ("%spx" % self.font_size) if self.font_size else font.size
        font.family = self.font_family or font.family
        font.line_height = self.font_line_height or font.line_height
        return font

    def get_standard_font_style(self):
        self.ensure_one()
        font = self.get_font()
        style = ""
        if font.line_height:
            style += ";line-height:" + font.line_height
        if font.family:
            style += ";font-family:" + font.family
        if font.size:
            style += ";font-size:" + font.size
        return style

    @staticmethod
    def get_amount_in_text(obj, field_name, currency_field='currency_id'):
        currency_id = getattr_new(obj, currency_field)
        if not currency_id:
            return ""

        amount = getattr_new(obj, field_name)
        text = currency_id.amount_to_text(amount)
        return text
#
#     def get_other_option_data(self, technical_name):
#         self.ensure_one()
#         for each in self.section_other_option_ids:
#             if each.name_technical == technical_name:
#                 return each.get_value()
#         return False

    def get_option_data(self, technical_name):
        self.ensure_one()

        for line in self.line_ids.filtered(lambda x: x.type == "options"):
            for each in line.option_field_ids:
                if each.name_technical == technical_name:
                    return each.get_value()

    def get_signature_data(self, technical_name):
        self.ensure_one()
        line_id = self.line_ids.filtered(lambda x: x.type == "signature_boxes" and x.name_technical == technical_name)
        if line_id:
            return line_id[0].signature_box_ids
        return False

    def get_report_list(self):
        """Hook"""
        return {}

#     @api.model
#     def create(self, vals):
#         res = super(ReportingTemplate, self).create(vals)
#         if not res.section_2_model_id:
#             res.section_2_model_id = res.model_id.id
#         return res
#
    def get_page_no_section(self):
        self.ensure_one()
        if self.page_number_type == "none":
            return ""
        return """Page: <span class="page"/> / <span class="topage"/>"""

    @staticmethod
    def _hasattr(obj, attribute):
        return hasattr(obj, attribute)

    def get_header_footer_images(self, image_type, name_technical, company_id):
        self.ensure_one()
        line_id = self.line_ids.filtered(lambda x: x.name_technical == name_technical)
        if not line_id:
            return False

        line = line_id.header_footer_img_ids.filtered(lambda x: x.company_id.id == company_id.id)
        if not line:
            return False

        return getattr(line[0], image_type) or False

    def get_header_image(self, name_technical, company_id):
        self.ensure_one()
        return self.get_header_footer_images("header", name_technical, company_id)

    def get_footer_image(self, name_technical, company_id):
        self.ensure_one()
        return self.get_header_footer_images("footer", name_technical, company_id)






class ReportingTemplateTemplateTemplate(models.Model):
    _name = 'report.custom.template.template'

    name = fields.Char(required=True)
    name_technical = fields.Char(required=True)
    report_name = fields.Char()
    parameters = fields.Text()
#     color1 = fields.Char()
#     color2 = fields.Char()
#     color3 = fields.Char()
    image = fields.Binary()

    def parameter_values(self):
        self.ensure_one()
        import ast
        return ast.literal_eval(self.parameters)


# class ReportingTemplateHeaderSection(models.Model):
#     _name = 'reporting.custom.template.header.field'
#
#     report_id = fields.Many2one('reporting.custom.template')
#     sequence = fields.Integer('Sequence', default=10)
#     prefix = fields.Selection(SEPARATORS, string='Start With')
#     field_id = fields.Many2one('ir.model.fields', domain=[('model_id.model', '=', 'res.company')])
#     field_type = fields.Selection('Field Type', related='field_id.ttype', readonly=True)
#     field_relation = fields.Char(related='field_id.relation', readonly=True)
#     field_display_field_id = fields.Many2one('ir.model.fields', string="Display Field", domain="[('model_id.model', '=', field_relation)]")
#     # display_field_name = fields.Char(string='Display Field') # Archived
#     label = fields.Char(string='Label')
#
#
# class ReportingTemplateFooterSection(models.Model):
#     _name = 'reporting.custom.template.footer.field'
#
#     report_id = fields.Many2one('reporting.custom.template')
#     sequence = fields.Integer('Sequence', default=10)
#     field_id = fields.Many2one('ir.model.fields', domain=[('model_id.model', '=', 'res.company')])
#     field_type = fields.Selection('Field Type', related='field_id.ttype', readonly=True)
#     field_relation = fields.Char(related='field_id.relation', readonly=True)
#     field_display_field_id = fields.Many2one('ir.model.fields', string="Display Field", domain="[('model_id.model', '=', field_relation)]")
#     # display_field_name = fields.Char(string='Display Field')
#     label = fields.Char(string='Label')
#
#
# class ReportingTemplatePartnerSection(models.Model):
#     _name = 'reporting.custom.template.partner.field'
#
#     report_id = fields.Many2one('reporting.custom.template')
#     sequence = fields.Integer('Sequence', default=10)
#     prefix = fields.Selection(SEPARATORS, string='Start With')
#     field_id = fields.Many2one('ir.model.fields', domain=[('model_id.model', '=', 'res.partner')])
#     field_type = fields.Selection('Field Type', related='field_id.ttype', readonly=True)
#     field_relation = fields.Char(related='field_id.relation', readonly=True)
#     field_display_field_id = fields.Many2one('ir.model.fields', string="Display Field", domain="[('model_id.model', '=', field_relation)]")
#     # display_field_name = fields.Char(string='Display Field')
#     label = fields.Char(string='Label')
#
#
# class ReportingTemplateSection2(models.Model):
#     _name = 'reporting.custom.template.section.2'
#
#     report_id = fields.Many2one('reporting.custom.template')
#     sequence = fields.Integer('Sequence', default=10)
#     model_id = fields.Many2one('ir.model', related='report_id.section_2_model_id', readonly=True)
#     field_id = fields.Many2one('ir.model.fields', domain="[('model_id', '=', model_id)]")
#     field_type = fields.Selection('Field Type', related='field_id.ttype', readonly=True)
#     field_relation = fields.Char(related='field_id.relation', readonly=True)
#     field_display_field_id = fields.Many2one('ir.model.fields', string="Display Field", domain="[('model_id.model', '=', field_relation)]")
#     label = fields.Char(string='Label')
#     null_value_display = fields.Boolean(string='Display Null')
#
#
class ResCompany(models.Model):
    _inherit = 'res.company'

    @staticmethod
    def get_template_report_font_assets():
        body = ""
        for each in get_all_font_list(with_extension=True):
            body += """@font-face {font-family: '%s'; src: URL('/report_utils2/static/fonts/%s') format('truetype');}
            """ % (rchop(each[0], ".ttf"), each[0])
        return "<style>%s</style>" % body


# class ReportingCustomTemplateSignBox(models.Model):
#     _name = 'reporting.custom.template.sign.box'
#
#     report_id = fields.Many2one('reporting.custom.template')
#     heading = fields.Char(string="Heading")
#     sequence = fields.Integer('Sequence', default=10)
