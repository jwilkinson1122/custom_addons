# -*- coding: utf-8 -*-

from . import models
from . import report

from odoo import api, SUPERUSER_ID



def set_qr_code(env):
    product_env = env['product.product'].search([])
    for record in product_env:
        name = record.name.replace(" ", "")
        record.sequence = 'DEF' + name.upper()+str(record.id)
        record.generate_qr()
            
# def set_qr_code(cr):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     for record in env['product.product'].search([]):
#         name = record.name.replace(" ", "")
#         record.sequence = 'DEF' + name.upper()+str(record.id)
#         record.generate_qr()

# def set_qr_code(cr):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     product_env = env['product.product'].with_env(env(cr.dbname))
#     for record in product_env.search([]):
#         name = record.name.replace(" ", "")
#         record.sequence = 'DEF' + name.upper() + str(record.id)
#         record.generate_qr()

 
 
