# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "POS Customer's Favorites",
  "summary"              :  """The module allows you to see previously bought products in the POS. The user can see the list of the most frequent products purchased by the customer.""",
  "category"             :  "Point of Sale",
  "version"              :  "1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-POS-Customer-s-Favorites.html",
  "description"          :  """POS Customer's Favourites
POS Customer's Favourites Products
POS Customer's Favourite Items
Customer Frequently Purchased Products
Customer Mostly Purchased Module
Sort Product by Customer Sales
Odoo POS Customer's Favorites
POs most bought products
Customer product list POS
Frequently purchased product POS
All product list POS""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_customer_favorites&custom_url=/pos/auto",
  "depends"              :  [
                             'point_of_sale',
                             'product',
                            ],
  "data"                 :  [
                             'views/pos_customer_favorites_view.xml',
                             'views/template.xml',
                             'security/ir.model.access.csv',
                            ],
  "demo"                 :  ['data/pos_customer_favorites_demo.xml'],
  "qweb"                 :  ['static/src/xml/pos_customer_favorites.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  39,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}