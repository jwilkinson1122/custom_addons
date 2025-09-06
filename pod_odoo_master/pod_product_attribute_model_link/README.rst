============================
Product Attribute Model Link
============================

This module allows to link product attributes to models and populate attribute values from the model 
records and vice versa. When a record is created in a model that is linked to an attribute new attribute 
value will be created automatically. When a record that is linked to an attribute value is deleted 
linked attribute value will be deleted if it is not used or archived otherwise. If a related record field 
value linked to an attribute value is updated the attribute value name is updated accordingly. If a module 
that implements a model linked to attribute(s) is uninstalled all the linked attribute values remain in place.


Use Cases / Context
===================

Sometimes you would like to create product variants based on other model values. 

For example you have a "T-Shirt" product in which two attributes are used among others: "design" and "material".

At the same time you store information about both of them in your db in the dedicated models.

"Design" model keeps the information about image print name, image print category, image author and stores the image file.

"Material" model keeps the information about material name, material type (synthetic/natural), material density and stores a handling instruction in pdf.

Using the regular Odoo flow one will need to create attributes for design and materials and then add values to them.

Eg "Material: cotton, silk, wool", "Design: Fancy Clown, Doge, Pepe, See beach"

And also add the same records to the "Materials" and "Design" models.

Configuration
=============

Go to the "Inventory/Configuration/Products/Attributes" menu and select an existing or create a new attribute.

Following configuration fields are available:

- Linked Model: 
    - Model which records will be used for the attribute values. 
    - Cannot be a transient model. 
    - Warning: changing or removing existing value will not affect existing attribute values!

- Linked Field: 
    - Field of the selected model that will be used for the attribute value names. 
    - Can be any field except for related or computed non-stored ones. Digital field values will be converted to Char automatically.
    - Warning: changing or removing existing value will not affect existing attribute values!

- Domain (optional): 
    - If configured only records matching the domain will be used for attribute value creation. 
    - Warning: updating domain will not affect existing attribute values!

- Add to Products on Create: 
    - If enabled when a new attribute value is created it will be automatically added to all existing products that use this attribute. 
    - Attention! You must completely understand possible consequences and use this option with care!

- Create from Attribute Values: 
    - If enabled when a new attribute value is added to the attribute a new record will be created in the linked model. 
    - Attention! The only value passed explicitly on creation will be the linked field containing the new attribute value name. 
    - You must ensure that this would be enough for new record creation. Otherwise an exception will be raised. 
    - If a digital field is used a conversion attempt will be done. 
    - If conversion fails an exception might be raised.

- Modify from Attribute Values: 
    - If enabled when an attribute value is renamed linked field value in the linked model will be updated accordingly.
    - If a digital field is used a conversion attempt will be done. 
    - If conversion fails an exception might be raised.
    - This option is available only if "Create from Attribute Values" option is enabled.

- Delete when Attribute Value is Deleted: 
    - When enabled if an attribute value is deleted linked record will be deleted too. Use with extreme care! 
    - This option is available only if "Create from Attribute Values" option is enabled.



Creating, modifying or deleting related records from attributes requires corresponding access rights to linked model. Otherwise access error will occur.

There is no "Attribute/Model" restriction so you can link several attributes to the same model. 

You can use same records and fields or apply custom domains to fine tune such mappings.

When adding a model mapping to an attribute with existing values you can map those manually in the attribute value list.

Usage
=====

Create, modify or delete a record in a model that is linked to an attribute(s). 
Linked attribute values will be added, modified, deleted or archived accordingly.

Create, modify or delete an attribute value. 
Linked model records will be modified accordingly in case such options are enabled for the attribute.

