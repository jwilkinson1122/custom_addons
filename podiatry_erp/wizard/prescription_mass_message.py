import logging
from odoo import api, exceptions, fields, models


_logger = logging.getLogger(__name__)


class PrescriptionMassMessage(models.TransientModel):
    _name = "prescription.massmessage"
    _description = "Send Message to Borrowers"

    prescription_ids = fields.Many2many(
        "medical.prescription",
        string="Prescriptions",
    )
    message_subject = fields.Char()
    message_body = fields.Html()

    @api.model
    def default_get(self, field_names):
        defaults_dict = super().default_get(field_names)
        # Add values to the defaults_dict here
        prescription_ids = self.env.context["active_ids"]
        defaults_dict["prescription_ids"] = [(6, 0, prescription_ids)]
        return defaults_dict

    def button_send(self):
        import pdb
        pdb.set_trace()
        self.ensure_one()
        if not self.prescription_ids:
            raise exceptions.UserError(
                "No Prescriptions were selected."
            )
        if not self.message_body:
            raise exceptions.UserError(
                "A message body is required"
            )
        for prescription in self.prescription_ids:
            prescription.message_post(
                body=self.message_body,
                subject=self.message_subject,
                subtype_xmlid='mail.mt_comment',
            )
            _logger.debug(
                "Message on %d to followers: %s",
                prescription.id,
                prescription.message_follower_ids,
            )

        _logger.info(
            "Posted %d messages to the Prescriptions: %s",
            len(self.prescription_ids),
            str(self.prescription_ids),
        )
        return True
