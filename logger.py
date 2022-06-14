import logging
from datetime import datetime
import sys
from os import getcwd, environ
from selenium.webdriver.remote.remote_connection import LOGGER as SERVERLOGGER

# --------- Global config ----------- #
SERVERLOGGER.setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
environ["WDM_LOG"] = "0"
current_dir = getcwd()

# --------- LOGGING CONFIG ---------- #
timestamp = datetime.now().strftime("%d-%b-%H-%M-%S")
formatter = logging.Formatter('[%(levelname)s][%(asctime)s] %(message)s','%d-%m-%y %H:%M:%S')
stdOutformatter = logging.Formatter('[%(levelname)s][%(asctime)s] %(message)s','%H:%M:%S')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

output_handler = logging.FileHandler(f"{current_dir}/Logs/Log-{timestamp}.log",encoding='utf-8')
output_handler.setFormatter(formatter)
output_handler.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(stdOutformatter)
stdout_handler.setLevel(logging.INFO)
# stdout_handler.setLevel(logging.DEBUG)

logger.addHandler(output_handler)
logger.addHandler(stdout_handler)

def changeLevel(level):
    levels={'DEBUG':logging.DEBUG,'INFO':logging.INFO}
    stdout_handler.setLevel(levels[level])
    logging.info(f'Log level changed to {level}')