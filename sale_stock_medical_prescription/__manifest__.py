# Copyright 2016 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': 'Medical Prescription Sale Stock',
    'summary': 'Provides dispense logic for prescriptions.',
    'author': 'LabViv',
    'version': '13.0.0.0.1',
    'website': 'https://labviv.org.ve/',
    'license': 'GPL-3',
    'category': 'Medical',
    'installable': True,
    'post_init_hook': '_update_medicament_type',
    'depends': [
        'sale_stock',
        'sale_medical_prescription',
    ],
    'data': [
        'data/stock_data.xml',
        'views/stock_warehouse_view.xml',
        'views/prescription_order_line_view.xml',
    ],
    'demo': [],
    'maintainer': 'Reydi Hernández <rhe@mastercore.net>'
}
