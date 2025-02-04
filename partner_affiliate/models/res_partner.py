from odoo import fields, models, api, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    # ---------------------------------------------------------------------
    # Affiliates
    # ---------------------------------------------------------------------

    affiliate_ids = fields.One2many(
        'res.partner',
        'parent_id',   
        string='Affiliates',
        compute='_compute_affiliates',
        help="Direct and indirect affiliates",
        compute_sudo=True,
        store=True
    )
    
    affiliate_all_count = fields.Integer('Indirect Affiliates Count',
        compute='_compute_affiliates', recursive=True, store=False, compute_sudo=True)

    @api.depends('parent_id')
    def _compute_affiliates(self):
        for partner in self:
            affiliates = partner._get_affiliates(parents=self.env['res.partner'])
            partner.affiliate_ids = affiliates
            partner.affiliate_all_count = len(affiliates)

    def _get_affiliates(self, parents=None, visited=None):
        if visited is None:
            visited = self.env['res.partner']
        if not parents:
            parents = self.env[self._name]

        indirect_affiliates = self.env[self._name]
        parents |= self

        direct_affiliates = self.affiliate_ids - parents
        # Prevent infinite loops
        direct_affiliates = direct_affiliates - visited
        visited |= direct_affiliates

        child_affiliates = direct_affiliates._get_affiliates(parents=parents, visited=visited) if direct_affiliates else self.browse()
        indirect_affiliates |= child_affiliates
        return indirect_affiliates | direct_affiliates

    def open_affiliate_form(self):
        """Open affiliate contact form from the parent partner form view"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    # ---------------------------------------------------------------------
    # Contacts
    # ---------------------------------------------------------------------

    child_ids = fields.One2many(
        'res.partner',
        'parent_id',  
        string='Contacts',
        compute='_compute_children',
        help="Direct and Indirect Contacts",
        compute_sudo=True,
        store=True
    )

    child_all_count = fields.Integer('Indirect Contacts Count',
        compute='_compute_children', recursive=True, store=False, compute_sudo=True)

    @api.depends('parent_id')
    def _compute_children(self):
        for partner in self:
            children = partner._get_children(parents=self.env['res.partner'])
            partner.child_ids = children
            partner.child_all_count = len(children)

    def _get_children(self, parents=None, visited=None):
        if visited is None:
            visited = self.env['res.partner']
        if not parents:
            parents = self.env[self._name]

        indirect_children = self.env[self._name]
        parents |= self

        direct_children = self.child_ids - parents
        # Prevent infinite loops
        direct_children = direct_children - visited
        visited |= direct_children

        child_children = direct_children._get_children(parents=parents, visited=visited) if direct_children else self.browse()
        indirect_children |= child_children
        return indirect_children | direct_children

    def open_child_form(self):
        """Open child contact form from the parent partner form view"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }