from odoo import models, api, fields
from datetime import datetime

class ProductTemplate(models.Model):
  _inherit = 'pos.order'

  def action_receipt_to_customer_WTS(self, name, client, ticket):
    if not self:
      return False

    # TODO : send attachment to customer, trhough whatsapp
    return True

    