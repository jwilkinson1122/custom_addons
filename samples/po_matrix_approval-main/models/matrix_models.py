from odoo import api, fields, models, _
from datetime import datetime

class MatriksApproval(models.Model):
    _name = 'matriks.approval'

    name = fields.Char(string='Name')
    model_id = fields.Many2one('ir.model', string='Model')
    line_ids = fields.One2many('matriks.approval.line', 'approval_id', string='Lines')

class MatriksApprovalLine(models.Model):
    _name = 'matriks.approval.line'
    _description = 'Matriks Approval Line'

    approval_id = fields.Many2one('matriks.approval', string='Approval')
    group_id = fields.Many2one('res.groups', string='Group')
    sequence = fields.Integer(string='Sequence')

class PurchaseOrderApprovalHistory(models.Model):
    _name = 'purchase.order.approval.history'
    _description = 'List of Approved Orders'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    user_id = fields.Many2one('res.users', string='User')
    group_id = fields.Many2one('res.groups', string='Group')
    date = fields.Datetime(string='Date')
    note = fields.Text(string='Note')

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    approval_history_ids = fields.One2many('purchase.order.approval.history', 'purchase_order_id', string='Approved Lines')
    is_visible_button = fields.Boolean('Show Operation Buttons', default=True)

    def _get_matriks_approval_group(self):
        model_id = self.env['ir.model'].sudo().search([('name', '=', 'matriks.approval')], limit=1)
        group_id = self.env['res.groups'].sudo().search([
            # ('users', 'in', [self.env.user.id]),
            ('model_access.model_id', '=', model_id.id)
        ])
        if group_id:
            return group_id
        else:
            return False

    @api.onchange('partner_id')
    def _onchange_visibility(self):
        matriks_approval_group = self._get_matriks_approval_group()

        if matriks_approval_group:
            print("User has access to confirm a purchase order based on the matriks_approval_group")
        else:
            print("User has no access to confirm a purchase order based on the matriks_approval_group")


    def button_confirm(self):
        res = super(PurchaseOrderInherit, self).button_confirm()
        matriks_approval_group = self._get_matriks_approval_group()
        po_approval_model = self.env['purchase.order.approval.history'].sudo()

        if matriks_approval_group:
        #     self.is_visible_button = True
        #     print("User has access to confirm a purchase order based on the matriks_approval_group")
        #     return res
        # else:
        #     self.is_visible_button = False
        #     print("User has no access to confirm a purchase order based on the matriks_approval_group")
        #     return {'type': 'ir.actions.act_window_close'}

        # if self.env.user.has_group('matrix_approval.access_matrix_approval'):
            po_approval_model.create({
                'purchase_order_id': self.id,
                'user_id': self.env.user.id,
                'group_id': matriks_approval_group.id,
                'date': datetime.now(),
                'note': f'Approved by {self.env.user.name} at {datetime.now().strftime("%d-%m-%Y")} for unconditional reason.'
            })
            return res
        else:
            return {
                'name': _('Access Denied'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': self.env.ref('matrix_approval.wizard_simple_form').id,
                'view_type': 'form',
                'res_model': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_message': _('You do not have the required access to confirm the Purchase Order.'),
                },
            }

    def button_cancel(self):
        res = super(PurchaseOrderInherit, self).button_cancel()
        matriks_approval_group = self._get_matriks_approval_group()
        po_approval_model = self.env['purchase.order.approval.history'].sudo()

        if matriks_approval_group:
            print("User has access to cancel a purchase order based on the matriks_approval_group")
            po_approval_model.create({
                'purchase_order_id': self.id,
                'user_id': self.env.user.id,
                'group_id': matriks_approval_group.id,
                'date': datetime.now(),
                'note': f'Canceled by {self.env.user.name} at {datetime.now().strftime("%d-%m-%Y")} for unconditional reason.'
            })
            return res
        else:
            print("User has no access to cancel a purchase order based on the matriks_approval_group")
            return {'type': 'ir.actions.act_window_close'}
