# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    additional_hours = fields.Integer(
        help="Provide the min hours value for \
                                      book in, book_out days, whatever the \
                                      hours will be provided here based on \
                                      that extra days will be calculated.",
    )