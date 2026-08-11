"""
Central place for locating secrets that live OUTSIDE this project directory.

Nothing here ever prints, logs, or returns the raw secret values except the
one function that hands the Gemini key to the SDK client. No secret is ever
written into a file inside this project.
"""

import os
from pathlib import Path

from dotenv import dotenv_values

GEMINI_ENV_PATH = Path("/home/user/Swinfy/API/geminiapikey.env")
TWITTER_COOKIES_PATH = Path("/home/user/Swinfy/Twitter/cookies.json")

# The key inside geminiapikey.env is spelled "GEMIN_API_KEY" (not GEMINI_).
_GEMINI_KEY_NAME = "GEMIN_API_KEY"


class ConfigError(RuntimeError):
    pass


def get_gemini_api_key() -> str:
    if not GEMINI_ENV_PATH.exists():
        raise ConfigError(f"Gemini credentials file not found at {GEMINI_ENV_PATH}")
    values = dotenv_values(GEMINI_ENV_PATH)
    key = values.get(_GEMINI_KEY_NAME) or os.environ.get(_GEMINI_KEY_NAME)
    if not key:
        raise ConfigError(
            f"{_GEMINI_KEY_NAME} not found in {GEMINI_ENV_PATH}. "
            "Add it there — never hard-code it in the app."
        )
    return key


def get_cookies_path() -> str:
    if not TWITTER_COOKIES_PATH.exists():
        raise ConfigError(f"Twitter cookies file not found at {TWITTER_COOKIES_PATH}")
    return str(TWITTER_COOKIES_PATH)
