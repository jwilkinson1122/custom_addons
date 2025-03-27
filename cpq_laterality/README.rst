===========
cpq_laterality
===========

Adds the ability for large numbers of colors / laterality / options on product
variants, as a custom option, rather than a very large number of attribute
values.

This is useful to help group custom options for pricing, whilst still providing
a fixed list.

Leverages the cpq module as a basis.

Use cases
=========

- Laterality or Edging on orthotic
- A very large fixed list of fabric colors

Usage
=====

1. Goto Product > Configuration > Laterality
2. Create your Laterality records. Organize them into parent/child relationships.
   The parents will be selectable on the product variant UI.
3. Goto Product > Configuration > Attributes
4. Create or edit an attribute, select the `Is custom` option, change the `CPQ
   custom type` to `Laterality`, and select the Laterality parent to use as the basis
   for a list.
5. When configuring a product you will now be prompted for a value from Laterality
   to select. This will be propagated into the product custom options.
