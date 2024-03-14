# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Technologies(odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0
#    (OPL-1) It is forbidden to publish, distribute, sublicense, or
#    sell copies of the Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
#    OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
#    THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
###############################################################################
{
    'name': "Product Add-ons in POS",
    'version': '17.0.0.0.0',
    'summary': """ Add product addons(flavour) to the product in POS.""",
    'description': "This module brings an option to add addon(extension)"
                   " cost of the products in the point of sale. You can "
                   "configure the addon as a product, so it brings all the"
                   " product features to the add-on. It is simple to handle"
                   " by choosing the add-on from the side bar menu which "
                   "doesn't affect your product screen. It shows the add-on "
                   "cost in the receipt.",
    'author': "Cybrosys Techno Solutions",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'category': 'Point of Sale',
    'depends': ['pos_restaurant'],
    'data': [
        'views/product_addons_view.xml',
    ],
    'assets': {
            'point_of_sale.assets': [
                'pos_product_addons/static/src/js/product_addons.js',
                'pos_product_addons/static/src/js/models.js',
                'pos_product_addons/static/src/js/orderline.js',
                'pos_product_addons/static/src/js/multiprint.js',
                'pos_product_addons/static/src/css/product_addons_style.css',
                'https://riversun.github.io/jsframe/jsframe.js'
            ],
            'web.assets_qweb': [
                'pos_product_addons/static/src/xml/product_addons_template_view.xml',
                'pos_product_addons/static/src/xml/multiprint.xml',
            ],
        },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'price': 19.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
}
