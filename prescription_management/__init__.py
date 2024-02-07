# -*- coding: utf-8 -*-


from . import models
from . import controllers
from odoo.tools import column_exists, create_column


def pre_init_hook(env):
    """Do not compute the prescription_template_id field on existing RXs."""
    if not column_exists(env.cr, "prescription", "prescription_template_id"):
        create_column(env.cr, "prescription", "prescription_template_id", "int4")

def uninstall_hook(env):
    res_ids = env['ir.model.data'].search([
        ('model', '=', 'ir.ui.menu'),
        ('module', '=', 'prescription')
    ]).mapped('res_id')
    env['ir.ui.menu'].browse(res_ids).update({'active': False})


def post_init_hook(env):
    res_ids = env['ir.model.data'].search([
        ('model', '=', 'ir.ui.menu'),
        ('module', '=', 'prescription'),
    ]).mapped('res_id')
    env['ir.ui.menu'].browse(res_ids).update({'active': True})
