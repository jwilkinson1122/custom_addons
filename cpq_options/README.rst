===========
cpq_options
===========

Adds the ability for large numbers of colors /  options on product
variants, as a custom option, rather than a very large number of attribute
values.

This is useful to help group custom options for pricing, whilst still providing
a fixed list.

Leverages the cpq module as a basis.

Use cases
=========

- Options for custom orthotics
- A very large fixed list of fabric colors

Usage
=====

1. Goto Product > Configuration > Options
2. Create your Options records. Organize them into parent/child relationships.
   The parents will be selectable on the product variant UI.
3. Goto Product > Configuration > Attributes
4. Create or edit an attribute, select the `Is custom` option, change the `CPQ
   custom type` to `Options`, and select the Options parent to use as the basis
   for a list.
5. When configuring a product you will now be prompted for a value from the option
   to select. This will be propagated into the product custom options.
