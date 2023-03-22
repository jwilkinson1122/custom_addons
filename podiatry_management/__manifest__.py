# -*- coding: utf-8 -*-
{
    "name": "Product Management Interface",
    "version": "15.0.1.0.6",
    "category": "Sales",
    "author": "faOtools",
    "website": "https://faotools.com/apps/15.0/product-management-interface-598",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "product"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
        "wizard/change_prm_category.xml",
        "wizard/update_prm_attributes.xml",
        "wizard/update_prm_followers.xml",
        "wizard/update_prm_product_type.xml",
        "wizard/update_prm_price.xml",
        "wizard/update_prm_optional_products.xml",
        "wizard/copy_values_from_template.xml",
        "views/product_template.xml",
        "views/menu.xml",
        "data/data.xml"
    ],
    "assets": {
        "web.assets_backend": [
                "podiatry_management/static/src/js/product_kanbancontroller.js",
                "podiatry_management/static/src/js/product_kanbanmodel.js",
                "podiatry_management/static/src/js/product_kanbanrecord.js",
                "podiatry_management/static/src/js/product_kanbanrender.js",
                "podiatry_management/static/src/js/product_kanbanview.js",
                "podiatry_management/static/src/css/styles.css"
        ],
        "web.assets_qweb": [
                "podiatry_management/static/src/xml/*.xml"
        ]
},
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to search, select and mass update product templates. Category tree. Tags hierarchy. Attributes tree. Product kanban navigator. Product catalog",
    "description": """For the full details look at static/description/index.html
* Features * 
- Configurable mass actions for product templates
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
    "price": "149.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=86&ticket_version=15.0&url_type_id=3",
}