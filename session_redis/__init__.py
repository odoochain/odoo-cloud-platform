from odoo.tools import config


def _patch_system():
    if "session_redis" in config.get("server_wide_modules"):
        from . import http
        from . import session
        # from . import models

