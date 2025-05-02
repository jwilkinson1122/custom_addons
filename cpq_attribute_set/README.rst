=============
Attribute Set
=============


This module allows the user to create Attributes to any model.
This is a basic module in the way that **it does not provide views to display these new Attributes.**

Each Attribute created will be related to an **existing field** (in case of a *"native"* Attribute) or to a newly **created field** (in case of a *"custom"* Attribute).

A *"custom"* Attribute can be of any type : Char, Text, Boolean, Date, Binary... but also Many2one or Many2many.

In case of m2o or m2m, these attributes can be related to **custom options** created for the Attribute, or to **existing Odoo objects** from other models.

Last but not least an Attribute can be **serialized** using the Odoo SA module 'base_sparse_field'.
It means that all the serialized attributes will be stored in a single "JSON serialization field" and will not create new columns in the database (and better, it will not create new SQL tables in case of Many2many Attributes),  **increasing significantly the requests speed** when dealing with thousands of Attributes.

Usage
=====

Even if this module does not provide views to display some model's Attributes, it provides however a Technical menu in *Settings > Technical > Database Structure > Attributes* to **create new Attributes**.

An Attribute is related to both an Attribute Group and an Attribute Set :

- The **Attribute Set** is related to the *"model's category"*, i.e. all the model's instances which will display the same Attributes.
- The **Attribute Group** is related to the *"attribute's category"*. All the attributes from the same Attribute Set and Attribute Group will be displayed under the same field's Group in the model's view.


     🔎 In order to create a custom Attribute many2one or many2many related to **other Odoo model**, you need to activate the Technical Setting **"Advanced Attribute Set settings"** (:code:`group_advanced_attribute_set`).

-----

If you want to create a module displaying some specific model's Attributes :

1. Your model must **\_inherit the mixin** :code:`"attribute.set.owner.mixin"`
2. You need to **add a placeholder** :code:`<separator name="attributes_placeholder" />` at the desired location in the model's form view.
3. Finally, **add a context** :code:`{"include_native_attribute": True}` on the action leading to this form view if the model's view needs to display attributes related to native fields together with the other "custom" attributes.
