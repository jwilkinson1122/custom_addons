# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Attachment Thumbnail View (Community)',
    'version': '1.0',
    'summary': 'This module allows to display thumbnail view for attachments.',
    'category': 'Document',
    'price': 12,
    'currency': 'EUR',
    'description': """
This module allows to display thumbnail view for attachments.
    """,
    'author' : 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'depends': ['base', 'mail'],
    'data' : [
        'views/ir_attachement_view.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}