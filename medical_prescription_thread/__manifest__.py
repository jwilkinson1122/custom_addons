# Copyright 2015 LasLabs
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': 'Medical Prescription Threaded',
    'summary': 'Adds message threading to Prescription Orders.',
    'version': '13.0.0.0.1',
    'category': 'Medical',
    'depends': ['medical_prescription'],
    'author': 'LabViv',
    'website': 'https://labviv.org.ve/',
    'license': 'GPL-3',
    'data': [
        'views/medical_prescription_order_view.xml',
        'views/medical_prescription_order_line_view.xml'
    ],
    'installable': True,
    'maintainer': 'Reydi Hernández <rhe@mastercore.net>'
}
