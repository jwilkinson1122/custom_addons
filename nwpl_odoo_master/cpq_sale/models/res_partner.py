from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    picking_note = fields.Html(
        string="Picking Internal Note",
        help="The notes will be added to the sales order and"
        "pickings but will not be printed "
        "on the delivery slip.",
    )
    picking_customer_note = fields.Text(
        string="Picking Customer Comments",
        help="The notes will be added to the sales order and"
        "pickings and will be printed on "
        "the delivery slip.",
    )
    
    
    def name_get(self):
        result = []
        show_clean = self.env.context.get("show_clean_name", False)
        for rec in self:
            if show_clean and (rec.is_contact or rec.is_patient):
                # Just show the contact/patient's name
                name = rec.name or ''
            elif (rec.is_contact or rec.is_patient) and rec.parent_id:
                # Default fallback: show parent name prefix if available
                name = f"{rec.parent_id.name}, {rec.name}"
            else:
                name = rec.name or ''
            result.append((rec.id, name))
        return result
    
    def _compute_display_name(self):
        show_clean = self.env.context.get("show_clean_name", False)
        for partner in self:
            if show_clean and (partner.is_contact or partner.is_patient):
                partner.display_name = partner.name or ''
            else:
                partner.display_name = super(Partner, partner)._get_complete_name()
