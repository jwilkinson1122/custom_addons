# -*- coding: utf-8 -*-
from . import controllers, models, wizards
from . import base_user_role
from . import base_user_role_company
from . import pod_contacts
from . import pod_product_attribute_archive
from . import pod_product_attribute_model_link
from . import pod_brand
from . import pod_product_brand
from . import pod_flexible_bom
from . import pod_pos_product_options
from . import pod_pos_order_customizations
from . import pod_pos_measurements
from . import pod_pos_theme_responsive
from . import pod_pos_wh_stock
from . import pod_pos_remove_cart_item
from . import pod_pos_counter, pod_pos_create_so, pod_pos_create_po, pod_pos_order_label
# from . import pod_prescription_order
from . import pod_pos_order_list
from . import pod_pos_receipt_extend
from . import pod_pos_product_variant
from . import pod_pos_keyboard_shortcut
from . import pod_pos_order_discount
from . import pod_pos_product_suggestion
from . import pod_pos_product_code
from . import pod_pos_cash_in_out
from . import pod_pos_hide_cash_control
from . import pod_base_order_type, pod_pos_order_type
from . import pod_product_multi_barcode, pod_pos_multi_barcode
from . import pod_product_configurator
from . import pod_product_configurator_sale
from . import pod_prescription_order
from . import pod_product_configurator_prescription_order
from . import pod_product_configurator_mrp

from .hooks import post_init_hook

# from .hooks import set_sale_price_on_variant

