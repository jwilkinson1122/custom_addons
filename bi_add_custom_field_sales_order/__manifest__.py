# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Add Custom Fields on Sales Order Form',
    'version' : '15.0.0.0',
    'category' : 'Sales',
    'summary': 'Easy to add custom field on sale Form Add custom field on sales Form add custom field on SO custom field quotation custom fields add custom fields on Sale order view edit sales model edit sales order view edit sale form edit sale order view',
    'description': """
        BrowseInfo developed a new odoo/OpenERP module apps
        Easy to add custom field on Quotation Form.
        Add custom field on Sale Order Form
        Add custom field on Sales order form
        Develop custom module, Develop custom field.
        sale order custom fields
        quotation custom fields
        sales order custom fields
        add custom fields on sales order form
        add custom fields on sales order view
        add custom fields on sales order form
        add custom fields on sales order view

        add custom fields on sale order form
        add custom fields on sale order view
        add custom fields on sale order form
        add custom fields on sale order view

        add custom fields on quotation form
        add custom fields on quotation view
        add custom field on quotation form
        add custom field on quotation view
        Easy Customize form, Edit sale view, edit sale order view, edit form. edit sales order form, edit quotation form, edit contact form.edit quote form, edit sale view.edit view.
    """,
    'author': 'Browseinfo',
    'website' : 'https://www.browseinfo.com',
    'price': '25.00',
    'currency': "EUR",
    'depends' : ['base','sale','sale_management'],
    'data' :[
                'security/saleorder_custom_groups.xml',
                'security/ir.model.access.csv',
                'views/saleorder_custom_field_view.xml',
                        
            ],      
    'qweb':[],
    'auto_install': False,
    'installable': True,
    'live_test_url':'https://youtu.be/DZtAatMqNXg',
    "images":['static/description/Banner.png'],
    "license": "OPL-1",
}



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
