#coding: utf-8

import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class product_template(models.Model):
    """
    Re-write to add methods required by js interface
    """
    _inherit = "product.template"

    @api.depends("attribute_line_ids", "attribute_line_ids.attribute_id", "attribute_line_ids.value_ids")
    def _compute_attribute_value_to_search_ids(self):
        """
        Compute method for attribute_value_to_search_ids
        """
        for templ in self:
            values = templ.attribute_line_ids.mapped("value_ids")
            templ.attribute_value_to_search_ids = [(6, 0, values.ids)]

    attribute_value_to_search_ids = fields.Many2many(
        "product.attribute.value",
        "product_attribute_value_product_template_rel_table",
        "product_attribute_value_id",
        "product_template_id",
        string="All possible values",
        compute=_compute_attribute_value_to_search_ids,
        store=True,
    )

    def return_selected_products(self):
        """
        The method to return selected products

        Returns:
         * list of 2 lists & boolean:
          ** dicts of products values requried for mass operations
          ** dicts of mass actions
          ** whether export is turned on
        """
        self = self.with_context(lang=self.env.user.lang)
        products = []
        for product in self:
            products.append({
                "id": product.id,
                "name": product.name_get()[0][1],
            })
        actions = self._return_mass_actions()
        Config = self.env['ir.config_parameter'].sudo()
        export_conf = safe_eval(Config.get_param("pod_hms_export_option", "False"))
        return [products, actions, export_conf]

    def rerurn_all_pages_ids(self, domain):
        """
        The method to search products by js domain

        Returns:
         *  list of all products articles
        """
        all_articles = set(self.ids + self.search(domain).ids)
        return list(all_articles)

    @api.model
    def _return_mass_actions(self):
        """
        The method to return available mass actions in js format

        Returns:
         * list of dict
           ** id
           ** name
        """
        self = self.sudo()
        Config = self.env['ir.config_parameter']
        mass_actions = safe_eval(Config.get_param("pod_hms.ir_actions_server_ids", "[]"))
        self = self.with_context(lang=self.env.user.lang)
        res = []
        for action in mass_actions:
            action_id = self.env["ir.actions.server"].browse(action)
            try:
                if action_id.id:
                    res.append({
                        "id": action,
                        "name": action_id.name,
                    })
            except:
                _logger.warning("The action {} has been deleted".format(action))
        return res

    def proceed_mass_action(self, action):
        """
        The method to trigger mass action for selected products

        Args:
         * action - ir.actions.server id

        Methods:
         * run() of ir.actions.server
        """
        context = self.env.context.copy()
        active_ids = self.ids
        context.update({
            "active_id": self.ids[0],
            "active_ids": self.ids,
            "active_model": "product.template"
        })
        res = self.env["ir.actions.server"].browse(action).with_context(context).run()
        if res:
            if res.get("view_id"):
                res = {
                    "view_id": res.get("view_id")[0], 
                    "res_model": res.get("res_model"), 
                    "display_name": res.get("display_name"),
                }
            elif res.get("type").find("ir.actions") != -1:
                res = {"action": res}
        return res

    @api.model
    def return_eshop_categories_hierarchy(self):
        """
        The method to return hierarchy of e-shop categories in jstree format
        DUMMY method to be implemented in pod_hms _website_sale
        """
        return []
