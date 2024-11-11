# -*- coding: utf-8 -*-

import base64

from odoo import api, tools, SUPERUSER_ID
from odoo.modules.module import get_resource_path


def post_init_hook(env):

    def get_binary(file_name, module, path="static/img"):
        """Helper function to encode file as base64 binary data."""
        file_path = get_resource_path(module, path, file_name)
        with tools.file_open(file_path, "rb") as f:
            return base64.b64encode(f.read())

    # Set up initial data for the 'Bad Bertrix Club'
    env.ref("website.default_website").write(
        {
            "name": "Bad Bertrix Club",
            "logo": get_binary(
                "bbc92_logo_notext_white_small.jpg", "profile_badbertrixclub"
            ),
        }
    )

    env.ref("base.main_partner").write(
        {
            "name": "Bad Bertrix Club",
            "email": "badbertrixclub92@gmail.com",
            "image_1920": get_binary("bbc92_logo.jpg", "profile_badbertrixclub"),
        }
    )

    env.ref("base.main_company").write(
        {
            "account_sale_tax_id": False,
        }
    )


# def post_init_hook(env):

#     def get_binary(file_name, module='profile_badbertrixclub', path='static/img'):
#         file_path = get_resource_path(module, path, file_name)
#         with tools.file_open(file_path, 'rb') as f:
#             return base64.b64encode(f.read())

#     env.ref('website.default_website').write({
#         'name': 'Bad Bertrix Club',
#         'logo': get_binary('bbc92_logo_notext_white_small.jpg'),
#     })

#     env.ref('base.main_partner').write({
#         'name': 'Bad Bertrix Club',
#         'email': 'badbertrixclub92@gmail.com',
#         'image_1920': get_binary('bbc92_logo.jpg'),
#     })
#     env.ref('base.main_company').write({
#         'account_sale_tax_id': False,
#     })
