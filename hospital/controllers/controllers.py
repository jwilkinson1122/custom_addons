# -*- coding: utf-8 -*-
from odoo import http
import json

class Hospital(http.Controller):
    @http.route('/hospital/hospital/', auth='public',website=True)
    def index(self, **kw):
        return "hello odoo"

    @http.route('/hospital/medicine', auth='public')
    def list(self, **kw):
        medicines=http.request.env['hospital.medicine'].search([])
        print(medicines)
        all_result=[]
        for med in medicines:
            one_record={
               'name': med.name,
                'description':med.description,
                'usage_type':med.usage_type ,
                'barcode':med.barcode,
                'sale_price':med.sale_price,
                'scientific_name':med.scientific_name,
                'originator':med.originator,
                'taxes':med.taxes,
                'order_serial':[i.medicine_order_seq for i in med.order_serial],
                'sale_price_after_taxes':med.sale_price_after_taxes,
                'stock_start':med.stock_start,
                'quantity_available':med.quantity_available,
                'quantity_sold':med.quantity_sold
            }
            # print(f"{dir(med.order_serial.medicine_name.order_serial.medicine_order_seq)}")
            # print("////////////////////////")
            all_result.append(one_record)

        # print(all_result)
        # test=[{'name': 'Chanda Bond', 'description': 'Alias vero qui conse', 'usage_type': 'aqua', 'barcode': '123843755', 'sale_price': 900.0, 'scientific_name': 'Blair Dorsey', 'originator': 'Distinctio Dolor de', 'taxes': 1.0, 'order_serial': hospital.sale.medicine(), 'sale_price_after_taxes': 1800.0, 'stock_start': 100, 'quantity_available': 0.0, 'quantity_sold': 0.0}, {'name': 'Carson Mosley', 'description': 'Quaerat id iure reru', 'usage_type': 'aqua', 'barcode': 'Velit Nam in pariat', 'sale_price': 25.0, 'scientific_name': 'Hollee Tillman', 'originator': 'Velit qui veritatis', 'taxes': 1.0, 'order_serial': hospital.sale.medicine(1, 5), 'sale_price_after_taxes': 50.0, 'stock_start': 100, 'quantity_available': 699.0, 'quantity_sold': 699.0}]
        return json.dumps(all_result)
        # return http.request.render('hospital.list',{'hassan':22})

    @http.route('/hospital2/', auth='public')
    def object(self, **kw):
        return http.request.render('hospital.object', {
            'object': 'obj'
        })
#