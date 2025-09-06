# -*- coding: utf-8 -*-

from odoo import models, fields


class UserUtilities(models.Model):
    """This class is used to deal with tasks"""

    _name = "user.utilities"
    _description = "User Utilities"

    user_id = fields.Many2one("res.users", string="User")
    task_title = fields.Char(required=True, string="Title", help="For title")
    date = fields.Datetime(required=True, string="Date", help="Date field")
    calendar_event_id = fields.Many2one(
        "calendar.event", string="Calendar Event", ondelete="set null"
    )
