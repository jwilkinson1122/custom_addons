# from openupgradelib import openupgrade


# @openupgrade.migrate(use_env=True)
# def migrate(env, version):
#     view = env.ref('account_multicompany_ux.res_config_settings_view_form', raise_if_not_found=False)
#     if view:
#         view.unlink()

from odoo.upgrade import util


from odoo import api, SUPERUSER_ID


# def migrate(cr, version):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     for company in env['res.company'].search([('chart_template', '=', 'fr')]):
#         env['account.chart.template'].try_loading('fr', company)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    view = env.ref('account_multicompany_ux.res_config_settings_view_form', raise_if_not_found=False)
    if view:
        view.unlink()