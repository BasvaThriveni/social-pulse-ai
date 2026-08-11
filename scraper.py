"""
Thin wrapper around the existing, working scraper at
/home/user/Swinfy/Twitter/scrape_recent_tweets.py.

We deliberately do NOT rewrite that scraper — we import its functions
directly so any future fixes made there are picked up automatically.
"""

import importlib.util
import sys
from pathlib import Path

import pandas as pd

from .config import get_cookies_path

_SCRAPER_PATH = Path("/home/user/Swinfy/Twitter/scrape_recent_tweets.py")
_MODULE_NAME = "swinfy_scrape_recent_tweets"


class ScrapeError(RuntimeError):
    pass


def _load_scraper_module():
    if _MODULE_NAME in sys.modules:
        return sys.modules[_MODULE_NAME]
    if not _SCRAPER_PATH.exists():
        raise ScrapeError(f"Scraper script not found at {_SCRAPER_PATH}")
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, _SCRAPER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


def fetch_recent_tweets(username: str, count: int) -> list[dict]:
    """Fetch the most recent `count` original tweets for `username`.

    Returns a list of dicts (tweet_id, created_at, text, likes, retweets,
    replies, views, url). Raises ScrapeError on any failure with a
    user-friendly message.
    """
    username = username.lstrip("@").strip()
    if not username:
        raise ScrapeError("Please enter a valid X/Twitter username.")

    module = _load_scraper_module()
    cookies_path = get_cookies_path()

    try:
        rows = module.get_recent_tweets(
            username, count=count, cookies_path=cookies_path, headless=True
        )
    except ValueError as e:
        raise ScrapeError(str(e)) from e
    except TimeoutError as e:
        raise ScrapeError(
            f"Timed out fetching @{username}'s tweets. The profile may be "
            "private, rate-limited, or slow to load. Try again shortly."
        ) from e
    except Exception as e:
        raise ScrapeError(f"Could not fetch tweets for @{username}: {e}") from e

    if not rows:
        raise ScrapeError(
            f"No original tweets found for @{username}. The account may have "
            "no recent posts, or only pinned/retweeted content."
        )
    return rows


def tweets_to_dataframe(rows: list[dict]) -> pd.DataFrame:
    columns = ["tweet_id", "created_at", "text", "likes", "retweets", "replies", "views", "url"]
    df = pd.DataFrame(rows, columns=columns)
    return df
