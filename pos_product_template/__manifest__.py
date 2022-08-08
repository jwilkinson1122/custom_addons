{
    "name": "POS - Product Template",
    "version": "14.0.1.0.1",
    "category": "Point Of Sale",
    "author": "Akretion,Odoo Community Association (OCA)",
    "summary": "Manage Product Template in Front End Point Of Sale",
    "website": "https://github.com/OCA/pos",
    "license": "AGPL-3",
    "depends": [
        "point_of_sale",
    ],
    # C:\odoo15\server\odoo\custom_addons\pos_product_template\static\src\xml\ppt.xml
    "data": [
        # "static/src/xml/ppt.xml",
        # "static/src/xml/SelectVariantPopup.xml",
        # "view/assets.xml",
    ],

    "assets": {
        "web.assets_backend": {
            "pos_product_template/static/src/css/ppt.css",
            "pos_product_template/static/src/js/ppt.js",
            "pos_product_template/static/src/js/models.js",
            "pos_product_template/static/src/js/SelectVariantPopup.js",
        }
    },

    "qweb": [
        "static/src/xml/ppt.xml",
        "static/src/xml/SelectVariantPopup.xml",
    ],
    "demo": [
        "demo/product_attribute_value.xml",
        "demo/product_product.xml",
    ],
    "images": [
        "static/src/img/screenshots/pos_product_template.png",
    ],
    "installable": True,
}
