# -*- coding: utf-8 -*-
{
    "name": "prescription_management",
    "summary": "Short (1 phrase/line) summary of the module's purpose",
    "description": """
Long description of module's purpose
    """,
    "author": "My Company",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "mail", "account", "prescription"],
    # always loaded
    "data": [
        # 'security/prescription_management_groups.xml',
        "security/ir.model.access.csv",
        "data/ir_data_sequence.xml",
        "views/room_booking_views.xml",
        "views/prescription_menu_view.xml",
        "views/prescription_room_views.xml",
        "views/prescription_floor_views.xml",
        "views/prescription_product_views.xml",
        "views/prescription_amenity_views.xml",
        "views/prescription_service_views.xml",
        # 'views/account_move_views.xml',
        "views/repair_team_views.xml",
        "views/repair_request_views.xml",
        "views/orthotic_model_views.xml",
        # 'views/prescription_product_views.xml',
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
    "application": True,
}
