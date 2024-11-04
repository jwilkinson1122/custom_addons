""" Patient access revised to make the team staff relationship central to
access. Everything is calculated from there. Inverse functions deal with
sports.team.staff records instead of having a separate table for storing
access rights."""

from odoo import api, SUPERUSER_ID, Command


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rules = (
        env.ref("pod_practice_management.restrict_staff_access_to_teams")
        + env.ref("pod_practice_management.restrict_staff_access_to_team_injuries")
        + env.ref("pod_practice_management.restrict_staff_access_to_team_players")
    )
    rules.write({"groups": [Command.link(env.ref("base.group_user").id)]})
    env.ref("pod_practice_management.group_sports_clinic_user").write(
        {"implied_ids": [Command.link(env.ref("base.group_partner_manager").id)]}
    )
    cr.execute("DROP TABLE sports_team_res_users_rel")
    # Check the groups are OK
