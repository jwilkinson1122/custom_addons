# -*- coding: utf-8 -*-


from odoo import Command, api, models, modules


class Users(models.Model):
    _name = 'res.users'
    _inherit = ['res.users']

    @api.model
    def systray_get_activities(self):
        """ Update the systray icon of res.partner activities to use the
        contact application one instead of base icon. """
        activities = super(Users, self).systray_get_activities()
        for activity in activities:
            if activity['model'] != 'res.partner':
                continue
            activity['icon'] = modules.module.get_module_icon('contacts')
        return activities

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        for user in users:
            user.partner_id.company_ids = user.company_ids
        return users

    def write(self, vals):
        res = super(Users, self.with_context(from_res_users=True)).write(vals)
        if "company_ids" in vals:
            for user in self.sudo():
                commands = []
                company_ids_data = vals["company_ids"]
                if isinstance(company_ids_data, list) and user.partner_id.company_ids:
                    for item in company_ids_data:
                        if isinstance(item, (list | tuple)):
                            if item[0] == Command.LINK:
                                commands.append(item)
                            if item[0] == Command.SET:
                                for company_id in item[2]:
                                    commands.append(Command.link(company_id))
                        else:
                            commands.append(Command.link(item))
                    user.partner_id.company_ids = commands
        return res
