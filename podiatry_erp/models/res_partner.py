from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, exceptions, models, _
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError


class InheritedResPartner(models.Model):
    _inherit = 'res.partner'

    dob = fields.Date()
    age = fields.Integer(compute='_cal_age', store=True, readonly=True)
    is_location = fields.Boolean('Practice')
    is_patient = fields.Boolean('Patient')
    is_doctor = fields.Boolean('Doctor')
    prescription_count = fields.Integer(compute='get_prescription_count')

    web_work_process_id = fields.Many2one(
        "website.auto.sale", string="Website Workflow Process")

    def open_customer_prescriptions(self):
        for records in self:
            return {
                'name': _('Prescription History'),
                'view_type': 'form',
                'domain': [('customer', '=', records.id)],
                'res_model': 'medical.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_customer': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['medical.prescription'].search_count(
                [('customer', '=', records.id)])
            records.prescription_count = count

    @api.depends('dob')
    def _cal_age(self):
        for record in self:
            if record.dob:
                years = relativedelta(date.today(), record.dob).years
                record.age = str(int(years))
            else:
                record.age = 0

    def _get_next_ref(self, vals=None):
        return self.env["ir.sequence"].next_by_code("res.partner")

    @api.model
    def create(self, vals):
        if not vals.get("ref") and self._needs_ref(vals=vals):
            vals["ref"] = self._get_next_ref(vals=vals)
        return super(InheritedResPartner, self).create(vals)

    def copy(self, default=None):
        default = default or {}
        if self._needs_ref():
            default["ref"] = self._get_next_ref()
        return super(InheritedResPartner, self).copy(default=default)

    def write(self, vals):
        for partner in self:
            partner_vals = vals.copy()
            if (
                not partner_vals.get("ref")
                and partner._needs_ref(vals=partner_vals)
                and not partner.ref
            ):
                partner_vals["ref"] = partner._get_next_ref(vals=partner_vals)
            super(InheritedResPartner, partner).write(partner_vals)
        return True

    def _needs_ref(self, vals=None):
        """
        Checks whether a sequence value should be assigned to a partner's 'ref'

        :param vals: known field values of the partner object
        :return: true iff a sequence value should be assigned to the\
                      partner's 'ref'
        """
        if not vals and not self:  # pragma: no cover
            raise exceptions.UserError(
                _("Either field values or an id must be provided.")
            )
        # only assign a 'ref' to commercial partners
        if self:
            vals = {}
            vals["is_company"] = self.is_company
            vals["parent_id"] = self.parent_id
        return vals.get("is_company") or not vals.get("parent_id")

    @api.model
    def _commercial_fields(self):
        """
        Make the partner reference a field that is propagated
        to the partner's contacts
        """
        return super(InheritedResPartner, self)._commercial_fields() + ["ref"]
