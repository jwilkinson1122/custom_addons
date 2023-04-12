
{
    "name": "Product Variant Configurator",
    "summary": "Provides an abstract model for product variant configuration.",
    "version": "15.0.1.0.0",
    "category": "Product Variant",
    "license": "AGPL-3",
    "author": "AvanzOSC, Tecnativa, ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-variant",
    "depends": ["product"],
    "data": [
        "security/product_configurator_security.xml",
        "security/ir.model.access.csv",
        "views/product_configurator_attribute.xml",
        "views/inherited_product_template_views.xml",
        "views/inherited_product_product_views.xml",
        "views/inherited_product_category_views.xml",
        "views/inherited_product_attribute_views.xml",
    ],
}
