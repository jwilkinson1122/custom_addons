# Copyright 2008 Luis Falcon <falcon@gnuhealth.org>
# Copyright 2017 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': 'Medical Medicament',
    'summary': 'Introduce Medicament notion into the medical product',
    'version': '17.0.0.0.0',
    'category': 'Medical',
    'depends': ['medical'],
    'author': 'LabViv',
    'website': 'https://labviv.org.ve/',
    'license': 'GPL-3',
    'data': [
        'security/ir.model.access.csv',
        'data/medical_drug_form.xml',
        'data/medical_drug_route.xml',
        # 'data/WHO_products.xml',
        'views/product_product_view.xml',
        'views/medical_medicament_view.xml',
        'views/medical_drug_form_view.xml',
        'views/medical_drug_route_view.xml',
    ],
    'installable': True,
    'maintainer': 'Reydi Hernández <rhe@mastercore.net>'
}
