============================
Product Variant Configurator
============================

Provides an abstract model for product variant configuration. It provides the
basic functionality for presenting a table with the attributes of a template
and the possibility to select one of the valid values. You can try this
functionality creating a product variant directly selecting a product
template that has attributes.

This module also prevents in a configurable way the creation of the product
variants when defining the attributes and attribute values of the product
template.

Configuration
=============

(after installing `sale_management` application)

To configure the creation of the variants behaviour, you need to:

#. Go to ``Sales > Configuration > Settings``, and select "Attributes and
   Variants (Set product attributes (e.g. color, size) to sell variants)" on
   "Product Catalog" section.
#. Go to ``Sales > Catalog > Products``, and select a product.
#. On the Variants tab edit the value of the field ``Variant Creation``.
#. If you want to stop the automatic creation of the variant, and have the same
   behaviour for all the products in the same category, go to ``Inventory >
   Configuration > Product Categories``, select the category and check the checkbox
   ``Don't create variants automatically``.

Usage
=====

(after installing `sale_management` application)

#. Go to ``Sales > Catalog > Product Variants``.
#. Click on "Create" button for creating a new one.
#. On the field "Product Template", select a product template that has several
   attributes.
#. A table with the attributes of the template will appear below.
#. Select all the attribute values and click on "Save" button.
#. A new product variant will be created for that attributes.
#. An error will raise if there's another variant with the same attribute
   values or if you haven't filled all the required values.

**Developers**

To use product configurator:

#. The product.configurator is an abstract model, hence, to be used it must be
   inherited in your model:
#. If the model you're inheriting has ``name`` attribute, and it uses the
   related parameter you must override it.

::

    class AModel(models.Model):
        _inherit = ['module.model', 'product.configurator']
        name = fields.Char(related="delegated_field.related_field")

