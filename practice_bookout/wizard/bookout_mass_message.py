import logging
from odoo import api, exceptions, fields, models


_logger = logging.getLogger(__name__)


class BookoutMassMessage(models.TransientModel):
    _name = "practice.bookout.massmessage"
    _description = "Send Message to Borrowers"

    bookout_ids = fields.Many2many(
        "practice.bookout",
        string="Bookouts",
    )
    message_subject = fields.Char()
    message_body = fields.Html()

    @api.model
    def default_get(self, field_names):
        defaults_dict = super().default_get(field_names)
        # Add values to the defaults_dict here
        bookout_ids = self.env.context["active_ids"]
        defaults_dict["bookout_ids"] = [(6, 0, bookout_ids)]
        return defaults_dict

    def button_send(self):
        import pdb
        pdb.set_trace()
        self.ensure_one()
        if not self.bookout_ids:
            raise exceptions.UserError(
                "No Bookouts were selected."
            )
        if not self.message_body:
            raise exceptions.UserError(
                "A message body is required"
            )
        for bookout in self.bookout_ids:
            bookout.message_post(
                body=self.message_body,
                subject=self.message_subject,
                subtype_xmlid='mail.mt_comment',
            )
            _logger.debug(
                "Message on %d to followers: %s",
                bookout.id,
                bookout.message_follower_ids,
            )

        _logger.info(
            "Posted %d messages to the Bookouts: %s",
            len(self.bookout_ids),
            str(self.bookout_ids),
        )
        return True
