from datetime import timedelta

IP_DB_NAME = "ip.db"
IP_DB_PATH = f"{IP_DB_NAME}"
IP_DB_EXPIRE_TIME = timedelta(days=365)

PROXY_DB_NAME = "proxies.db"
PROXY_DB_PATH = f"{PROXY_DB_NAME}"
PROXY_DB_EXPIRE_TIME = timedelta(hours=2)

DEFAULT_OUTFILE = "iposint.json"
DEFAULT_LOG_FILE = "iposint"
