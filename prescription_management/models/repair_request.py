from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RepairRequest(models.Model):
    _name = "repair.request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "sequence"
    _description = "Repair request"

    sequence = fields.Char(
        string="Sequence",
        readonly=True,
        default="New",
        copy=False,
        tracking=True,
        help="Sequence for identifying the request",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("assign", "Assigned"),
            ("ongoing", "Repair"),
            ("support", "Waiting For Support"),
            ("done", "Completed"),
        ],
        string="State",
        default="draft",
        help="State of repair request",
    )
    repair_type = fields.Selection(
        selection=[
            ("room", "Room"),
            ("prescription", "Prescription"),
            ("orthotic", "Vehicle"),
        ],
        required=True,
        tracking=True,
        string="Repair Type",
        help="Choose what is to be cleaned",
    )
    room_id = fields.Many2one(
        "prescription.room", string="Room", help="Choose the room"
    )
    prescription = fields.Char(
        string="Prescription", help="Repair request space in prescription"
    )
    orthotic_id = fields.Many2one(
        "orthotic.model", string="Vehicle", help="Repair request from orthotic"
    )
    support_team_ids = fields.Many2many(
        "res.users", string="Support Team", help="Support team members"
    )
    support_reason = fields.Char(string="Support", help="Support Reason")
    description = fields.Char(string="Description", help="Description about the repair")
    team_id = fields.Many2one(
        "repair.team",
        string="Team",
        required=True,
        tracking=True,
        help="Choose the team",
    )
    head_id = fields.Many2one(
        "res.users",
        string="Head",
        related="team_id.team_head_id",
        help="Head of repair team",
    )
    assigned_id = fields.Many2one("res.users", string="Assigned To")
    domain_partner_ids = fields.Many2many("res.partner", string="Domain Partner")

    def action_assign_repair(self):
        self.update({"state": "assign"})

    def action_start_repair(self):
        self.write({"state": "ongoing"})

    def action_done_repair(self):
        self.write({"state": "done"})

    def action_assign_support(self):
        if self.support_reason:
            self.write({"state": "support"})
        else:
            raise ValidationError(_("Please Enter the reason"))

    def action_assign_assign_support(self):
        if self.support_team_ids:
            self.write({"state": "ongoing"})
        else:
            raise ValidationError(_("Please Choose a support"))

    def action_maintain_request(self):
        self.env["maintenance.request"].sudo().create(
            {
                "date": fields.Date.today(),
                "state": "draft",
                "type": self.repair_type,
                "orthotic_maintenance_id": self.orthotic_id.id,
            }
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": "Maintenance Request Sent Successfully",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
