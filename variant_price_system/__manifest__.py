# -*- coding: utf-8 -*-
{
    "name": "Advanced Variant Prices",
    "version": "18.0.1.0.3",
    "category": "Sales",
    "author": "faOtools",
    "website": "https://faotools.com/apps/17.0/advanced-variant-prices-17-0-variant-price-system-845",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "sale"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/product_template_attribute_value.xml"
    ],
    "assets": {},
    "demo": [
        
    ],
    "summary": "The tool to configure variant prices based on attributes coefficients and surpluses. Product price multiplier. Product price coefficient. Product price extra. Product price surplus. Multi prices. Price system. Own variant price. Product attribute pricing. Multiple variant prices. Dynamic variant price",
    "description": """For the full details look at static/description/index.html
- The module setup assumes updating the app after its installation
* Features * 
- Odoo advanced pricing formula
- Special case: Odoo independent variant prices
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
    "price": "98.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=2&ticket_version=17.0&url_type_id=3",
}