from odoo import models, api, fields


class TopCoverLength(models.Model):
    _name = "topcover.length"

    name = fields.Char(required=True)

class TopCoverMaterial(models.Model):
    _name = "topcover.material"

    name = fields.Char(required=True)


class TopCoverDensity(models.Model):
    _name = "topcover.density"

    name = fields.Char(required=True)

class TopCoverThickness(models.Model):
    _name = "topcover.thickness"

    name = fields.Char(required=True)

# access_topcover_shape,access_topcover_shape,model_shape,base.group_system,1,1,1,1
# access_topcover_type,access_topcover_type,model_type,base.group_system,1,1,1,1
# access_topcover_manufacturer,access_manufacturer,model_manufacturer,base.group_system,1,1,1,1
# access_topcover_brand,access_topcover_brand,model_brand,base.group_system,1,1,1,1
# access_topcover_collection,access_topcover_collection,model_collection,base.group_system,1,1,1,1
