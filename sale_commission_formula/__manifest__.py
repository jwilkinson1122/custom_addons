{
    "name": "Sale Commission Formula",
    "version": "15.0.1.0.0",
    "category": "Sale",
    "license": "AGPL-3",
    "summary": "Sale commissions computed by formulas",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": ["sale_commission"],
    "data": ["views/sale_commission_view.xml"],
    "assets": {
        "web.assets_backend": [
            "sale_commission_formula/static/src/css/sale_commission_formula.css",
        ],
    },
    "demo": ["demo/commission_demo.xml"],
    "installable": True,
}