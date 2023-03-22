# -*- coding: utf-8 -*-

from lxml import etree
from lxml.builder import E

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval


PARAMS = [
    ("podiatry_management_attributes_option", safe_eval, "False"),
    ("podiatry_management_export_option", safe_eval, "False"),
    ("podiatry_management_eshop_categories_option", safe_eval, "False"),
]
ALREADYADDEDFIELDS = [
                        "image_128", "categ_id", "type", "lst_price", "product_variant_count", "product_variant_ids",
                        "currency_id", "sale_ok", "purchase_ok", "purchase_ok", "qty_available", "uom_id",
                        "website_published",   
                    ]

class res_config_settings(models.TransientModel):
    """
    Overwrite to add own settings
    """
    _inherit = "res.config.settings"

    @api.onchange("module_podiatry_management_website_sale")
    def _onchange_module_podiatry_management_website_sale(self):
        """
        Onchange method for module_podiatry_management_website_sale
        """
        for conf in self:
            if not conf.module_podiatry_management_website_sale:
                conf.podiatry_management_eshop_categories_option = False

    podiatry_management_attributes_option = fields.Boolean(string="Filter by attribute values")
    podiatry_management_export_option = fields.Boolean(string="Export products")
    ir_actions_server_ids = fields.Many2many(
        "ir.actions.server",
        "ir_actions_server_res_config_setting_rel_table",
        "ir_actions_server_id",
        "res_config_setting_id",
        string="Mass actions",
        domain=[("model_id.model", "=", "product.template")],
    )
    module_podiatry_management_website_sale = fields.Boolean(string="E-commerce mass actions")
    module_podiatry_management_accounting = fields.Boolean(string="Accounting mass actions")
    module_podiatry_management_stock = fields.Boolean(string="Warehouse mass actions")
    module_podiatry_management_purchase = fields.Boolean(string="Purchase mass actions")
    podiatry_management_eshop_categories_option = fields.Boolean(string="Filter by eCommerce categories")
    kanban_fields_ids = fields.Many2many(
        "ir.model.fields",
        "ir_model_fields_res_config_setting_rel_table",
        "ir_model_fields_id",
        "res_config_settings_id",
        string="Kanban Fields",
    )

    @api.model
    def get_values(self):
        """
        Overwrite to add new system params
        """
        Config = self.env['ir.config_parameter'].sudo()
        res = super(res_config_settings, self).get_values()
        values = {}
        for field_name, getter, default in PARAMS:
            values[field_name] = getter(str(Config.get_param(field_name, default)))
        ir_actions_server_ids =  safe_eval(Config.get_param("podiatry_management.ir_actions_server_ids", "[]"))
        existing_ids = self.env["ir.actions.server"].search([("id", "in", ir_actions_server_ids)]).ids
        values.update({"ir_actions_server_ids": [(6, 0, existing_ids)]})
        kanban_fields_ids =  safe_eval(Config.get_param("podiatry_management.kanban_fields_ids", "[]"))
        field_ids = self.env["ir.model.fields"].search([("id", "in", kanban_fields_ids)]).ids
        values.update({"kanban_fields_ids": [(6, 0, field_ids)]})
        res.update(**values)
        return res

    def set_values(self):
        """
        Overwrite to add new system params
        """
        Config = self.env['ir.config_parameter'].sudo()
        super(res_config_settings, self).set_values()
        for field_name, getter, default in PARAMS:
            value = getattr(self, field_name, default)
            Config.set_param(field_name, value)
        Config.set_param("podiatry_management.ir_actions_server_ids", self.ir_actions_server_ids.ids)
        kanban_fields_ids =  safe_eval(Config.get_param("podiatry_management.kanban_fields_ids", "[]"))
        if kanban_fields_ids != self.kanban_fields_ids.ids:
            Config.set_param("podiatry_management.kanban_fields_ids", self.kanban_fields_ids.ids)
            self.sudo()._update_kanban_view(self.kanban_fields_ids)

    @api.model
    def _update_kanban_view(self, cfields):
        """
        The method to update the view of product.template kanban

        Args:
         * cfields - ir.model.fields recordset
        """
        view_id = self.env["ir.ui.view"].search([("key", "=", "prmnt_custom_product_template_kanban")], limit=1)
        if not view_id:
            xml_content = """
                <data>
                    <ul name="custom_properties" position="after"/>
                    <ul name="custom_checkboxes" position="after"/>
                </data>
            """
            values = {
                "arch": xml_content,
                "model": "product.template",
                "key": "prmnt_custom_product_template_kanban",
                "type": "kanban",
                "inherit_id": self.sudo().env.ref("podiatry_management.product_template_kanban_view").id,
            }
            view_id = self.env["ir.ui.view"].create(values)
        xml_content = ""
        xml_checkboxes = []
        xml_properties = []
        for cfield in cfields:
            if cfield.name not in ALREADYADDEDFIELDS:
                if cfield.ttype == "boolean":
                    attrs = {"widget": "boolean"}
                    xml_checkboxes.append(E.li(E.field(name=cfield.name, **attrs), cfield.field_description))
                else:
                    attrs = {}
                    if cfield.ttype in ["one2many", "many2many"]:
                        attrs.update({"widget": "many2many_tags"})
                    if cfield.ttype in ["html"]:
                        attrs.update({"widget": "html"})
                    xml_properties.append(E.li(cfield.field_description, ": ", E.field(name=cfield.name, **attrs)))

        xml_properties = E.ul(E.ul(*(xml_properties), name="custom_properties",),
                              name="custom_properties",
                              position="replace",
                        )
        xml_checkboxes = E.ul(E.ul(*(xml_checkboxes), name="custom_checkboxes",),
                              name="custom_checkboxes",
                              position="replace",
                        )
        xml_content += etree.tostring(xml_properties, pretty_print=True, encoding="unicode")
        xml_content += etree.tostring(xml_checkboxes, pretty_print=True, encoding="unicode")
        xml_content = u"<data>{}</data>".format(xml_content)
        view_id.write({"arch": xml_content})
