from . import controllers
from . import models
from . import helpers

import logging
from logging.handlers import RotatingFileHandler
import sys
from odoo.tools.config import config

cpq_logger = logging.getLogger("cpq")
cpq_logger.setLevel(logging.DEBUG)

cpq_logfile = config.get('cpq_logfile', r"C:\odoo17\server\cpq.log")
file_handler = RotatingFileHandler(cpq_logfile, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
file_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_formatter)

class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[95m",
    }
    RESET = "\033[0m"

    # def format(self, record):
    #     color = self.COLORS.get(record.levelname, self.RESET)
    #     record.levelname = f"{color}{record.levelname}{self.RESET}"
    #     return super().format(record)
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')



console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColorFormatter(file_formatter._fmt, file_formatter.datefmt))
console_handler.encoding = 'utf-8'  # Add this line

if not cpq_logger.hasHandlers():
    cpq_logger.addHandler(file_handler)
    cpq_logger.addHandler(console_handler)

cpq_logger.propagate = False