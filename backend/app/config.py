import os

DB_PATH = "/app/data/manager.db"

IS_CONFIGURED = False

def check_initial_setup_state():
    global IS_CONFIGURED
    if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
        IS_CONFIGURED = True
    else:
        IS_CONFIGURED = False
    return IS_CONFIGURED