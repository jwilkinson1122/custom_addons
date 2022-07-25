# Account Model Items

# Account detail items:
#   acct name
#   acct#
#   main phone#
#   fax#
#   isParent(bool)
#   parent acct#(),
#   main address
#   account type (clinic, distributor, hospital, sole practitioner, veteran affairs (VA), other)

# Additional addresses:
#   address name
#   contact
#   clinic/contact
#   state/province
#   zip/postal
#   country/region
#   address Type (bill to, ship to, primary, other)
#   city
#   street
#   Phone numbers: main, phone2, fax
#   Additional info: shipping method, freight terms
# Sub Accounts:


from odoo import models, fields, api, _


class pod_account(models.Model):
    _name = "pod.account"
    _description = 'pod account'
    _rec_name = 'account_id'

    # partner_id = fields.Many2one('res.partner', 'Doctor', required=True)
    # practice_partner_id = fields.Many2one(
    #     'res.partner', domain=[('is_practice', '=', True)], string=' Practice')
    # code = fields.Char('Id')
    # info = fields.Text('Extra Info')
