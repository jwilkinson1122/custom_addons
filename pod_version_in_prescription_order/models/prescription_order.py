

from odoo import fields, models, _, api


class PrescriptionOrder(models.Model):
    """Inherits Prescriptions"""
    _inherit = "prescription.order"

    is_version = fields.Boolean(string="Is Version",
                                help="For checking version or not")

    version_count = fields.Integer(string="Prescription Version Count",
                                   compute='_compute_version_ids',
                                   help="Count of version created")
    current_version_id = fields.Many2one("prescription.order",
                                         help="For creating versions")
    version_ids = fields.One2many("prescription.order",
                                  inverse_name="current_version_id",
                                  help="Versions created")

    def action_create_versions(self):
        """For creating the versions of the prescription order"""
        prescription_order_copy_id = self.copy()
        prescription_order_copy_id.is_version = True
        length = len(self.version_ids)
        prescription_order_copy_id.name = "%s-%s" % (self.name, str(length + 1))

        self.write({'version_ids': [(4, prescription_order_copy_id.id)]})

    @api.depends('version_ids')
    def _compute_version_ids(self):
        """For calculating the number of versions created"""
        for prescription in self:
            prescription.version_count = len(prescription.version_ids)

    def action_view_versions(self):
        """action for viewing versions"""
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "kanban,tree,form",
            "name": _("Prescription Order Versions"),
            "res_model": self._name,
            "domain": [('id', 'in', self.version_ids.ids)],
            "target": "current",
        }
        return action

    def action_confirm(self):
        """Override the confirm button of the prescription order for cancelling the
        other versions and making the current version main"""
        res = super().action_confirm()
        if not self.version_ids:
            parent_prescription = self.current_version_id
            versions = parent_prescription.mapped('version_ids').mapped('id')
            if versions:
                versions.append(parent_prescription.id)
            for version in parent_prescription.version_ids:
                if version.state == 'prescription':
                    # Updating the version name into main version name and
                    # other versions state into cancel
                    version.current_version_id.update({'is_version': True,
                                                       'state': 'cancel'})
                    version.update({'version_ids': versions,
                                    "name": version.current_version_id.name,
                                    'is_version': False})
                if version.state == 'draft':
                    version.update({'state': 'cancel'})
        else:
            if self.state == 'prescription':
                for prescription in self.version_ids:
                    prescription.update({'state': 'cancel'})
        return res
