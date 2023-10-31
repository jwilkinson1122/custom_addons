from .code import get_design_code_with_pfx

THICKNESS_UOM = 'mm'
MOLDING_PREFIX = 'Molding service'
COUNTER_DIE_NAME = 'Counter-Die'


def generate_die_name(device_cfg):
    return _generate_die_name(
        device_cfg,
        device_cfg.material_id,
        device_cfg.die_id.name,
        device_cfg.quantity_spare_dies,
        with_design_code_pfx=False,
        with_design_name=True,
    )


def generate_counter_die_name(device_cfg):
    return _generate_die_name(
        device_cfg,
        device_cfg.material_counter_id,
        COUNTER_DIE_NAME,
        device_cfg.quantity_counter_spare_dies,
        with_design_code_pfx=True,
        with_design_name=False,
    )


def generate_mold_name(device_cfg):
    design_code = get_design_code_with_pfx(device_cfg)
    return f'{MOLDING_PREFIX} {design_code}{device_cfg.sequence}'


def _generate_die_name(
    device_cfg,
    material,
    die_name,
    quantity,
    with_design_code_pfx=False,
    with_design_name=False,
):
    material_label = material.label
    design = device_cfg.design_id
    if with_design_code_pfx:
        design_code = get_design_code_with_pfx(device_cfg)
    else:
        design_code = device_cfg.design_id.code
    thickness = material.thickness
    code = f'{material_label} {die_name}'
    if with_design_name:
        code = f'{code}, {design.name}'
    code = f'{code}, {design_code}{device_cfg.sequence}, {thickness:g} {THICKNESS_UOM}'
    if quantity:
        code = f'{code}+ Spare {quantity} pcs'
    return code
