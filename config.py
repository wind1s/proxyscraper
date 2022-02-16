from datetime import timedelta

# TODO: Move config data to a json file and init global variables from that file.
# Rename this file to something like "configinit" or "readconfig".

IP_DB_NAME = "ip.db"
IP_DB_PATH = f"{IP_DB_NAME}"
IP_DB_EXPIRE_TIME = timedelta(days=365)

PROXY_DB_NAME = "proxies.db"
PROXY_DB_PATH = f"{PROXY_DB_NAME}"
PROXY_DB_EXPIRE_TIME = timedelta(hours=2)

DEFAULT_OUTFILE = "iposint.json"
DEFAULT_LOG_FILE = "iposint"
