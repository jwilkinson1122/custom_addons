from odoo import models, api, fields


class FrameMaterial(models.Model):
    _name = "frame.material"

    name = fields.Char(required=True)


class FrameShape(models.Model):
    _name = "frame.shape"

    name = fields.Char(required=True)


class FrameType(models.Model):
    _name = "frame.type"

    name = fields.Char(required=True)


class FrameManufacturer(models.Model):
    _name = "frame.manufacturer"

    name = fields.Char(required=True)


class FrameBrands(models.Model):
    _name = "frame.brand"

    name = fields.Char(required=True)
    image = fields.Binary("Image", max_width=1920, max_height=1920, widget=True)


class FrameBrands(models.Model):
    _name = "frame.collection"

    name = fields.Char(required=True)
    brand = fields.Many2one('frame.brand', string='Brand')
