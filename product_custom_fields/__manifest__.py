# -*- coding: utf-8 -*-
{
    "name": "Custom Fields for Products",
    "version": "15.0.1.0.3",
    "category": "Extra Tools",
    "author": "faOtools",
    "website": "https://faotools.com/apps/15.0/custom-fields-for-products-581",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "product",
        "custom_fields"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/custom_template_field.xml",
        "views/template_custom_type.xml",
        "views/res_config_settings.xml",
        "views/product_template.xml"
    ],
    "assets": {},
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to add new fields for Odoo product templates without any technical knowledge",
    "description": """For the full details look at static/description/index.html
* Features * 
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
    "price": "10.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=115&ticket_version=15.0&url_type_id=3",
}