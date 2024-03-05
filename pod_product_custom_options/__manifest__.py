# -*- coding: utf-8 -*-
{
  'name': 'NWPL - Product Custom Options',
  'summary': """Manage variant products without making their variants.""",
  'category': 'Prescriptions/Sales',
  'description':  """Product Custom Options""",
  'version':  '17.0.0.0.0',
  'author':  'NWPL',
  'license':  'LGPL-3',
  'website':  'https://www.nwpodiatric.com',
  'depends': [
      'pod_prescription_management',
      'sale_management',
      
      ],
  'data':  [
      'security/ir.model.access.csv',
      'views/custom_options_views.xml',
      'views/product_template_views.xml',
      'views/prescription_order_views.xml',
      'wizard/option_selection_wizard_views.xml'
      ],
  'demo': ['data/custom_options_demo.xml'],
  'images': ['static/description/icon.png'],
  'application': True,
  # 'pre_init_hook': 'pre_init_check',
}
