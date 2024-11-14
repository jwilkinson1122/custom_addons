# register protocols first
from . import odoo_file_system
from . import rooted_dir_file_system
from . import server_env
from .server_env import serv_config, setboolean

# then add normal imports
from . import models
from . import wizards

# from . import server_env
# from .server_env import serv_config, setboolean
