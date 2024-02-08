from odoo import api, fields, models, exceptions


class CustomerScreen(models.Model):
    _inherit = 'res.partner'

    new_parent_id = fields.Many2one('res.partner', 'Parent',
                                    help='select a parent for the child',
                                    domain="[('new_parent_id', '=', False),('type','=','contact')]")
    new_child_ids = fields.One2many('res.partner', 'new_parent_id',
                                    string='Child Customers')

    @api.model
    def fetch_data(self, partner_id):
        parent = self.browse(partner_id)
        children = parent.new_child_ids
        child = []
        data_parent = {'parent': {
            'name': parent.name,
            'image': parent.image_1920},
            'child': child}
        for rec in children:
            data_child = {'name': rec.name,
                          'id': rec.id,
                          'image': rec.image_1920}
            child.append(data_child)
        return data_parent

    def get_formview_action(self, access_uid=None):
        print('mmm3',self)
        res = super().get_formview_action(access_uid=access_uid)
        res.update({
            'type': 'ir.actions.act_window',
            'name': 'Partner',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'res_id': self.id,
        })
        return res
