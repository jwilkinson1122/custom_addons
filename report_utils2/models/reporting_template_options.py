# -*- coding: utf-8 -*-
from odoo import api, fields, models


def truncate_long_text(text):
    return text[:70] + (text[70:] and '...')


class ReportCustomTemplateOptionsField(models.Model):
    _name = 'report.custom.template.options.field'

    report_line_id = fields.Many2one('report.custom.template.line', ondelete='cascade')
    field_type = fields.Char(required=True, default='char')
    name_technical = fields.Char()
    name = fields.Char(string="Description")
    value_display = fields.Char(string="Value", compute="_compute_value_display")
    value_char = fields.Char()
    value_text = fields.Text()
    value_html = fields.Html()
    value_boolean = fields.Boolean()
    value_integer = fields.Integer()
    value_combo_box = fields.Many2one('report.custom.template.options.combo.box.item', domain="[('key', '=', key_combo_box)]")
    key_combo_box = fields.Char()
    value_image = fields.Binary()

    def get_value(self):
        self.ensure_one()
        if self.field_type == "char":
            return self.value_char or ""
        elif self.field_type == "text":
            return self.value_text or ""
        elif self.field_type == "boolean":
            return self.value_boolean
        elif self.field_type == "integer":
            return self.value_integer
        elif self.field_type == "combo_box":
            return self.value_combo_box and self.value_combo_box.name_technical or False
        elif self.field_type == "break":
            return ""
        elif self.field_type == "image":
            return self.value_image
        elif self.field_type == "html":
            return self.value_html
        return "Unknown"

    def _compute_value_display(self):
        for rec in self:
            value = rec.get_value()
            if rec.field_type == "boolean":
                value = value and "Yes" or "No"
            if value and rec.field_type == "text":
                value = truncate_long_text(value)
            if value and rec.field_type == "combo_box":
                value = rec.value_combo_box and rec.value_combo_box.name or "Undefined"
            if rec.field_type == "image":
                value = value and "Uploaded" or "No Image"
            if rec.field_type == "html":
                value = ""

            rec.value_display = str(value)


class ReportCustomTemplateOptionsComboBoxItem(models.Model):
    _name = 'report.custom.template.options.combo.box.item'

    name = fields.Char()
    name_technical = fields.Char()
    option_name_technical = fields.Char()
    key = fields.Char()


    # ARCHIVED
    @api.model
    def create(self, vals):
        res = super(ReportCustomTemplateOptionsComboBoxItem, self).create(vals)
        for each in res:
            if not each.key:
                each.key = each.option_name_technical
        return res

