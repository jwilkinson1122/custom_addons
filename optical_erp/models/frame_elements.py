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

# access_frame_shape,access_frame_shape,model_shape,base.group_system,1,1,1,1
# access_frame_type,access_frame_type,model_type,base.group_system,1,1,1,1
# access_frame_manufacturer,access_manufacturer,model_manufacturer,base.group_system,1,1,1,1
# access_frame_brand,access_frame_brand,model_brand,base.group_system,1,1,1,1
# access_frame_collection,access_frame_collection,model_collection,base.group_system,1,1,1,1
