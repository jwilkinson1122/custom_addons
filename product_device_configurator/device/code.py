COUNTER_DIE_PFX = 'P'


def generate_die_code(device_cfg):
    extra_code = device_cfg.material_id.code
    if device_cfg.finishing_id:
        extra_code = f'{extra_code}{device_cfg.finishing_id.code}'
    return _generate_code(device_cfg, extra_code)


def generate_mold_code(device_cfg):
    return _generate_code(device_cfg, _get_counter_die_sequence(device_cfg))


def generate_counter_die_code(device_cfg):
    cdie_seq = _get_counter_die_sequence(device_cfg)
    extra_code = f'{cdie_seq}{device_cfg.material_counter_id.code}'
    return _generate_code(device_cfg, extra_code)


def get_design_code_with_pfx(device_cfg):
    c = device_cfg
    die_code = device_cfg.die_id.code
    return f'{die_code or ""}{c.design_id.code}'


def _generate_code(device_cfg, extra_code):
    code = _get_base_code(device_cfg)
    code = f'{code}{extra_code}'
    ref = device_cfg.ref
    if ref:
        return _get_code_with_ref(code, device_cfg.ref)
    return code


def _get_base_code(device_cfg):
    seq = device_cfg.sequence
    ref = device_cfg.insert_die_ref or ''
    return f'{device_cfg.origin}{ref}{get_design_code_with_pfx(device_cfg)}{seq}'


def _get_code_with_ref(code, ref):
    return f'{code} / {ref}'


# Used by both counter die and mold.
def _get_counter_die_sequence(device_cfg):
    return f'P{device_cfg.sequence_counter_die}'
