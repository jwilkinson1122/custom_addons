# -*- coding: utf-8 -*-
{
    "name": "Child Customers Org Chart",
    "version": "17.0.0.0.0",
    "author": "Ashokpk",
    "category": "contact",
    "summary": "Child Customers Org Chart",
    "description": """Add a new parent field to the customer screen.
        From there, we can select the parent customers.
        If we select any parent in the customer, 
        then this child shouldn't be able to be selected as parent in any other customers.
        And also, if any child customer selects a contact as a parent, 
        then the parent selection field should hide from the parent customer screen.
        how the child list as a chart in the parent account screen.""",
    "depends": ["contacts","base"],
    "data": [
        'views/customer_screen_view.xml',
    ],
    "assets": {
        "web.assets_backend":[
            'child_customer_org_chart/static/src/css/style.css',
            'child_customer_org_chart/static/src/js/org_chart.js',
            'child_customer_org_chart/static/src/xml/org_chart.xml',
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
