

{
    "name": "Stock Request Template",
    "summary": """
        Create Templates for Stock Request Orders""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": ["stock_request"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_request_order_template.xml",
        "views/stock_request_template.xml",
        "views/stock_request_order.xml",
    ],
}
