# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	"name" : "Website Automated Order Processing",
	"version" : "15.0.0.0",
	"category" : "Website",
	'summary': 'Website auto workflow website sale auto workflow Automated Sale Order Processing quotation auto workflow quote auto processing auto confirm website order automatic sale order process website order auto process invoice auto processing auto sale process',
	"description": """
		
		Website Auto Complete Sale Order in odoo,
		Automatic sales Invoice Delivery confirmation processing in odoo,
		Automated Sale Order Processing in odoo,
		Automated Sale Order done picking in odoo,
		Automated Sale Order create an invoicing in odoo,
		Automated Sale Order Validate an invoicing in odoo,

	""",
	"author": "BrowseInfo",
	"website" : "https://www.browseinfo.com",
	"price": 24,
	"currency": 'EUR',
	"depends" : ['base','bi_automated_sale_order'],
	"data": [
		'security/ir.model.access.csv',
		'views/website_auto_sale_view.xml',
	],
	'qweb': [
	],
	"auto_install": False,
	"installable": True,
	'license': 'OPL-1',
	"live_test_url":'https://youtu.be/s0IjnptQM-g',
	"images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
