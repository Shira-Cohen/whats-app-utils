import os

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings


LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()

# צייני את הנתיב לתיקיית הבסיס (תיקיית הפרויקט הגדולה)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# צייני את הנתיב המלא לקובץ ה-.env
ENV_PATH = os.path.join(BASE_DIR, '.env')

# טעני את הקובץ .env
load_dotenv(dotenv_path=ENV_PATH)

def get_allow_origins():
    return os.getenv("ALLOWED_ORIGINS")


class PostgresConfig(BaseSettings):
    USERNAME: str
    PASSWORD: str
    HOST: str
    PORT: int
    NAME: str

    @property
    def connection_string(self):
        return f"postgresql+asyncpg://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def sync_connection_string(self):
        # סינכרוני (ל־sync engine)
        return f"postgresql://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    class Config:
        env_prefix = "DB_"
        case_sensitive = True


def get_postgres_config():
    return PostgresConfig()
