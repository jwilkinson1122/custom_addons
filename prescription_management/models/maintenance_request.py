from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MaintenanceTeam(models.Model):
    _name = "maintenance.request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "sequence"
    _description = "Maintenance Team"

    sequence = fields.Char(
        readonly=True,
        string="Sequence",
        copy=False,
        default="New",
        help="Sequence number for" " identifying maintenance" " request",
    )
    date = fields.Date(
        string="Date", help="Date of maintenance request", default=fields.Date.today
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("team_leader_approve", "Waiting For User Assign"),
            ("pending", "Waiting For User To " "Accept"),
            ("ongoing", "Ongoing"),
            ("support", "Waiting For Support"),
            ("done", "Done"),
            ("verify", "Pending For Verify"),
            ("cancel", "Canceled"),
        ],
        default="draft",
        string="State",
        help="State of maintenance request",
        tracking=True,
    )
    team_id = fields.Many2one(
        "maintenance.team",
        string="Maintenance Team",
        help="Team for which this request is assigned",
        tracking=True,
    )
    team_head_id = fields.Many2one(
        "res.users",
        related="team_id.user_id",
        string="Team Leader",
        help="Head of the maintenance team",
    )
    assigned_user_id = fields.Many2one(
        "res.users",
        string="Assigned User",
        tracking=True,
        help="User to whom the request is " "assigned",
    )
    type = fields.Selection(
        selection=[
            ("room", "Room"),
            ("orthotic", "Vehicle"),
            ("prescription", "Prescription"),
            ("repair", "Repair"),
        ],
        string="Type",
        help="The type for which the request is creating",
        tracking=True,
    )
    room_maintenance_ids = fields.Many2many(
        "prescription.room", string="Room Maintenance", help="Choose Room Maintenance"
    )
    repair_maintenance = fields.Char(
        string="Repair Maintenance", help="This is the Repair Maintenance"
    )
    orthotic_maintenance_id = fields.Many2one(
        "orthotic.model", string="Vehicle", help="Choose Vehicle"
    )
    support_team_ids = fields.Many2many(
        "res.users", string="Support Team", help="Choose Support Team"
    )
    support_reason = fields.Char(string="Support", help="Reason for adding Support")
    remarks = fields.Char(string="Remarks", help="Add Remarks")
    domain_partner_ids = fields.Many2many(
        "res.partner", string="Partner", help="For filtering Users"
    )
