# -*- coding: utf-8 -*-

from odoo import api, fields, models

class update_prm_followers(models.TransientModel):
    _name = "update.prm.followers"
    _inherit = "product.sample.wizard"
    _description = "Update followers"

    partner_to_add_ids = fields.Many2many(
        "res.partner",
        "res_partner_subscribe_prm_followers_rel_table",
        "res_partner_id",
        "update_prm_followers_id",
        string="Subscribe partners",
    )
    partner_to_exclude_ids = fields.Many2many(
        "res.partner",
        "res_partner_unsubscribe_prm_followers_rel_table",
        "res_partner_id",
        "update_prm_followers_id",
        string="Unsubscribe partners",
    )
    def _update_products(self, product_ids):
        """
        The method to prepare new vals for followers

        Args:
         * product_ids - product.template recordset

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        if self.partner_to_add_ids:
            product_ids.message_subscribe(partner_ids=self.partner_to_add_ids.ids)
        if self.partner_to_exclude_ids:
            product_ids.message_unsubscribe(partner_ids=self.partner_to_exclude_ids.ids)
