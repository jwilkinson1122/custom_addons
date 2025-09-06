# -*- coding: utf-8 -*-
from . import models
from . import wizards
# from odoo import api, SUPERUSER_ID


# def uninstall_hook(cr, registry):
#     """ Reset domain of native user act window.
#     """
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     env.ref('base.action_res_users').domain = []


# def uninstall_hook(env):
#     """ Reset domain of native user act window.
#     """
#     reset_user_domain = env.ref('base.action_res_users').domain = []
#     if not reset_user_domain:
#         raise UserError('Cannot reset the domain of the user action window. '
#                         'Please check the module installation or contact support.')