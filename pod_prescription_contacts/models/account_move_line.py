from odoo import fields, models, _, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    account_code = fields.Char(compute='get_account_code', string="Account code")

    @api.depends('partner_id','account_id')
    def get_account_code(self):
        """
            assign account number of partner if move line is receivable (Customers) or payable (Suppliers)
        """
        for account_move_line in self:
            if account_move_line.account_id.id == account_move_line.partner_id.commercial_partner_id.property_account_receivable_id.id or \
                    account_move_line.account_id.id == account_move_line.partner_id.commercial_partner_id.property_account_payable_id.id:                
                account_move_line.account_code = account_move_line.partner_id.commercial_partner_id.account_code
            else:
                account_move_line.account_code = ''