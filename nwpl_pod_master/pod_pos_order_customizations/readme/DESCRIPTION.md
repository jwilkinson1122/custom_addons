Provides an abstract model for product variant configuration. It
provides the basic functionality for presenting a table with the
attributes of a template and the possibility to select one of the valid
values. You can try this functionality creating a product variant
directly selecting a product template that has attributes.

This module also prevents in a configurable way the creation of the
product variants when defining the attributes and attribute values of
the product template.


This module also allows you to handle sale price at product variant level
(product.product) instead of product level (product.template), which is
the default.

It replaces the extra price configuration with a fix price that can be
modified on each variant independently, which allows setting absolute
prices instead of relative ones.

