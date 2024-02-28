# -*- coding: utf-8 -*-


from odoo import models


class PrescriptionMixin(models.AbstractModel):
    """
    Inherit this mixin to automatically create a `prescriptions.prescription` when
    an `ir.attachment` is linked to a record.
    Override this mixin's methods to specify an owner, a folder or tags
    for the prescription.
    """
    _name = 'prescriptions.mixin'
    _description = "Prescriptions creation mixin"

    def _get_prescription_vals(self, attachment):
        """
        Return values used to create a `prescriptions.prescription`
        """
        self.ensure_one()
        prescription_vals = {}
        if self._check_create_prescriptions():
            prescription_vals = {
                'attachment_id': attachment.id,
                'name': attachment.name or self.display_name,
                'folder_id': self._get_prescription_folder().id,
                'owner_id': self._get_prescription_owner().id,
                'partner_id': self._get_prescription_partner().id,
                'tag_ids': [(6, 0, self._get_prescription_tags().ids)],
            }
        return prescription_vals

    def _get_prescription_owner(self):
        return self.env.user

    def _get_prescription_tags(self):
        return self.env['prescriptions.tag']

    def _get_prescription_folder(self):
        return self.env['prescriptions.folder']

    def _get_prescription_partner(self):
        return self.env['res.partner']

    def _check_create_prescriptions(self):
        return bool(self and self._get_prescription_folder())
