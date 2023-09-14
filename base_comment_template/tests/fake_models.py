from odoo import models


def setup_test_model(env, model_cls):
    """Pass a test model class and initialize it."""
    model_cls._build_model(env.registry, env.cr)
    env.registry.setup_models(env.cr)
    env.registry.init_models(
        env.cr, [model_cls._name], dict(env.context, update_custom_fields=True)
    )


def teardown_test_model(env, model_cls):
    """Pass a test model class and deinitialize it."""
    if not getattr(model_cls, "_teardown_no_delete", False):
        del env.registry.models[model_cls._name]
    env.registry.setup_models(env.cr)


class ResUsers(models.Model):
    _name = "res.users"
    _inherit = ["res.users", "comment.template"]
    _teardown_no_delete = True
