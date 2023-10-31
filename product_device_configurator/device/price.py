from odoo import _
from odoo.exceptions import UserError
from odoo.tools import float_round

DIGITS = 2


def calc_die_price(device_cfg):
    adjusted_price = _calc_adjusted_price(device_cfg)
    return adjusted_price + _calc_finishing_price(device_cfg)


def calc_counter_die_price(device_cfg):
    pricelist = device_cfg.partner_id.property_device_pricelist_id
    return device_cfg.area_priced * pricelist.price_counter_die


def calc_mold_price(device_cfg):
    if _calc_is_mold_free(device_cfg):
        return 0.0
    die_price = calc_die_price(device_cfg)
    pricelist = device_cfg.partner_id.property_device_pricelist_id
    return die_price * pricelist.mold_of_die_perc / 100


def calc_price_per_sqm(device_cfg, price, digits=DIGITS):
    # NOTE. Here using entered area as we are using already calculated
    # price to calculate price per sqm.
    price_per_sqm = price / device_cfg.area
    return float_round(price_per_sqm, precision_digits=digits)


def calc_discount_percent(orig_price, discounted_price):
    if not orig_price:
        return 0
    return 100 * (orig_price - discounted_price) / orig_price


# Die helpers
def _calc_adjusted_price(device_cfg):
    price = _calc_material_price(device_cfg)
    if device_cfg.design_id.is_embossed:
        primary_design_price_adj = (
            _calc_primary_design_price(device_cfg) * device_cfg.embossed_design_perc / 100
        )
        price += primary_design_price_adj + _calc_embossed_base_design_price(device_cfg)
    return price


def _calc_finishing_price(device_cfg):
    return device_cfg.area_priced * device_cfg.finishing_id.price


def _calc_primary_design_price(device_cfg):
    price = _calc_pricelist_price_with_difficulty(device_cfg)
    return price + _calc_material_price(device_cfg)


def _calc_embossed_base_design_price(device_cfg):
    return _calc_pricelist_price_with_difficulty(
        device_cfg, design=device_cfg.design_id.design_base_embossed_id
    )


def _calc_material_price(device_cfg):
    return device_cfg.area_priced * device_cfg.material_id.price


def _calc_pricelist_die_price(device_cfg, design=None):
    partner = device_cfg.partner_id
    pricelist = partner.property_device_pricelist_id
    # TODO: handle when no pricelist is assigned to partner.
    design = design or device_cfg.design_id
    for item in pricelist.item_ids:
        if item.design_id == design:
            return device_cfg.area_priced * item.price
    raise UserError(
        _(
            "No Device Pricelist Price found for Design %(design)s. "
            + "Partner: %(partner)s",
            design=design.name,
            partner=partner.name,
        )
    )


def _calc_pricelist_price_with_difficulty(device_cfg, design=None):
    price = _calc_pricelist_die_price(device_cfg, design=design)
    return price * device_cfg.difficulty_id.coefficient


# Mold helpers


def _calc_is_mold_free(device_cfg):
    qty = device_cfg.quantity_dies_total
    pricelist = device_cfg.partner_id.property_device_pricelist_id
    qty_free = pricelist.quantity_die_mold_free
    return qty_free and qty >= qty_free
