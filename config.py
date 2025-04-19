from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Config:
    bot_token: str
    openai_key: str
    database_url: str

def load_config() -> Config:
    return Config(
        bot_token=os.getenv("BOT_TOKEN"),
        openai_key=os.getenv("OPENAI_API_KEY"),
        database_url=os.getenv("DATABASE_URL"),
    )
