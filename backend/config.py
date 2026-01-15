import os

import dotenv


class Settings:
    def __init__(self):
        dotenv.load_dotenv()

        self.database_url = os.getenv("DATABASE_URL") or "sqlite:///servers.db"
        self.debug_mode = os.getenv("DEBUG_MODE") == "true"


settings = Settings()
