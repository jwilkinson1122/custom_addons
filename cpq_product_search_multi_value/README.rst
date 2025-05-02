==========================
Product Search Multi Value
==========================

This module allows users to search products based on a list of default codes or barcodes.
It can be extended to other values if needed.

Configuration
=============

By default, the multi value search looks on default_code and barcode properties.
If you need to extend to other property, you just need to adapt the related system parameter: 'cpq_product_search_multi_value.search_field'.

Usage
=====

Go on the product search view and search on a list of default_code separated by a space.
The search must be based on "Multiple search" field.
