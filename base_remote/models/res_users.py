from threading import current_thread

from odoo import SUPERUSER_ID, api, models
from odoo.exceptions import AccessDenied
from odoo.service import wsgi_server
from odoo.tools import config


class ResUsers(models.Model):
    _inherit = "res.users"

    def _register_hook(self):
        """🐒-patch XML-RPC controller to know remote address."""
        super()._register_hook()
        original_fn = wsgi_server.application_unproxied

        def _patch(environ, start_response):
            current_thread().environ = environ
            return original_fn(environ, start_response)

        wsgi_server.application_unproxied = _patch

    @classmethod
    def _auth_check_remote(cls, login, method):
        """Force a method to raise an AccessDenied on falsey return."""
        with cls.pool.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            remote = env["res.users"].remote
            if not config["test_enable"]:
                remote.ensure_one()
        result = method()
        if not result:
            # Force exception to record auth failure
            raise AccessDenied()
        return result

    # Override all auth-related core methods
    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        return cls._auth_check_remote(
            login,
            lambda: super(ResUsers, cls)._login(db, login, password, user_agent_env),
        )

    @classmethod
    def authenticate(cls, db, login, password, user_agent_env):
        return cls._auth_check_remote(
            login,
            lambda: super(ResUsers, cls).authenticate(
                db, login, password, user_agent_env
            ),
        )
