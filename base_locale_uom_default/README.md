Locale - Default UoM
====================

This module adds a concept of a default unit of measure on languages, unique by
unit category type.

It also provides a method that can be used in fields to work from said defaults.

Configuration
=============

Set default unit of measures in the `Languages` menu in settings.

Usage
=====

Fields that want to implement the language default should use the provided
method, such as in the below example:

    class MyModel(models.Model):
        _name = 'my.model'
        time_uom_id = fields.Many2one(
            string='Time Units',
            comodel_name='uom.uom',
            default=lambda s: s.env['res.lang'].default_uom_by_category('Time'),
        )

Credits
=======

Contributors
------------

This version
------------
* Ángel Ramírez Isea <angel.ramirez.isea@yandex.com>

Original Contributors
---------------------
* Dave Lasley <dave@laslabs.com>

Maintainer
----------
This module is maintained by Asociaciones Cooperativas  de Procesamiento
Unificado Informático, R.S.; Simón Rodríguez para el Conocimiento Libre, R.S.;
y Soluciones Informáticas para el Desarrollo de Inclusión Social, R.S.

To contribute to this module, please visit https://labviv.org.ve.
