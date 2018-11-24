import importlib, sys

static_folder_found = importlib.util.find_spec('static') is not None
if static_folder_found:
    db_credentials_found = importlib.util.find_spec('static.config')
    if not db_credentials_found:
        print('No database setup found, script aborted.')
        sys.exit()
else:
    print('No database setup found, script aborted.')
    sys.exit()

from static.config import credentials
from db.Database import Database

WCA_Database = Database(
        credentials['db'],
        credentials['host'],
        credentials['user'],
        credentials['passwd'],
        socket=credentials.get('socket', None),
        port=credentials.get('port', 3306)
    )
