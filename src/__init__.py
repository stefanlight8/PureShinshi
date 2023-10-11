from os import getenv
from platform import uname

from dotenv import load_dotenv

__all__ = ['DISCORD_TOKEN']
load_dotenv(override=True)

if getenv("FORCE_MAIN_LEVEL") == 1 or "linux" in uname().system.lower():
    DISCORD_TOKEN: str = getenv("MAIN_DISCORD_TOKEN")
else:
    DISCORD_TOKEN: str = getenv("CANARY_DISCORD_TOKEN")
