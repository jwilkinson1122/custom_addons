# Copyright 2016 LasLabs Dave Lasley <dave@laslabs.com>
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': 'Medical Medicament Physical Attributes',
    'summary': 'Provides physical attribute codes for medical_medicament.',
    'version': '17.0.0.0.0',
    'category': 'Medical',
    'depends': ['medical_medicament'],
    'author': 'LabViv',
    'website': 'https://labviv.org.ve/',
    'license': 'GPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/medical_medicament_view.xml',
    ],
    'installable': True,
    'maintainer': 'Reydi Hernández <rhe@mastercore.net>'
}
