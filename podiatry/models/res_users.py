# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.model
    def create(self, vals):
        """Inherit Method to create user of group hcp or doctor."""
        vals.update({'employee_ids': False})
        res = super(ResUsers, self).create(vals)
        if self._context.get('hcp_create', False):
            hcp_group_ids = [
                self.env.ref('podiatry.group_podiatry_hcp').id,
                self.env.ref('base.group_user').id,
                self.env.ref('base.group_partner_manager').id]
            res.write({'groups_id': [(6, 0, hcp_group_ids)],
                       'company_id': self._context.get('podiatry_id'),
                       'company_ids': [(4, self._context.get('podiatry_id'))]})
        return res
