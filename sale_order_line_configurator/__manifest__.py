##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022 Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

{
    "name": "Sale Order line configurator",
    "summary": "Adds a product configurator on sale order line",
    "version": "14.0.1.0.1",
    "category": "Sale Workflow",
    "website": "https://gitlab.com/tawasta/odoo/sale-workflow",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale", "sale_management","sale_product_configurator", "web", "stock"],
    "data": [
        # "views/assets_backend.xml", 
        "views/sale_order.xml"
        ],
    "assets": {
        "web.assets_backend": [
            "/sale_order_line_configurator/static/src/js/list_renderer.js",
        ],
    },
}

                # src="/sale_order_line_configurator/static/src/js/list_renderer.js"

