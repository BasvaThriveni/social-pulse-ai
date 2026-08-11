"""
Gemini-powered analysis of a fetched batch of tweets.

Two entry points:
- analyze_profile(username, rows) -> dict with summary/topics/sentiment/
  insights/marketing sections
- ask_profile(username, rows, question) -> str answer, grounded ONLY in the
  fetched tweets (no outside knowledge)
"""

import json

from google import genai
from google.genai import types

from .config import get_gemini_api_key

MODEL_NAME = "gemini-flash-latest"

_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "A 3-5 sentence plain-English summary of what this account posts about and how.",
        },
        "main_topics": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-7 short topic/theme labels, most prominent first.",
        },
        "sentiment": {
            "type": "object",
            "properties": {
                "overall_tone": {"type": "string", "description": "One short phrase, e.g. 'Positive and promotional'."},
                "explanation": {"type": "string", "description": "1-2 sentences justifying the tone assessment."},
            },
            "required": ["overall_tone", "explanation"],
        },
        "key_insights": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-6 concrete, non-obvious observations about this account's posting behavior or audience signals.",
        },
        "marketing_insights": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-6 actionable content/marketing recommendations a brand or the account owner could act on.",
        },
    },
    "required": ["summary", "main_topics", "sentiment", "key_insights", "marketing_insights"],
}


class AIError(RuntimeError):
    pass


_client_singleton: genai.Client | None = None


def _client() -> genai.Client:
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = genai.Client(api_key=get_gemini_api_key())
    return _client_singleton


def _format_tweets_for_prompt(rows: list[dict]) -> str:
    lines = []
    for i, r in enumerate(rows, 1):
        lines.append(
            f"[{i}] ({r.get('created_at') or 'unknown date'}) "
            f"likes={r.get('likes')} retweets={r.get('retweets')} replies={r.get('replies')} views={r.get('views')}\n"
            f"    {r.get('text') or '(no text)'}"
        )
    return "\n".join(lines)


def analyze_profile(username: str, rows: list[dict]) -> dict:
    tweets_block = _format_tweets_for_prompt(rows)
    prompt = f"""You are a social media intelligence analyst. Analyze the following
{len(rows)} recent original posts from the X/Twitter account @{username} and produce
a structured analysis. Base your analysis strictly on the content, engagement
numbers, and patterns visible in these posts — do not invent facts about the
account that aren't supported by this data.

POSTS:
{tweets_block}

Return your analysis in the required JSON structure."""

    try:
        response = _client().models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_ANALYSIS_SCHEMA,
                temperature=0.4,
            ),
        )
    except Exception as e:
        raise AIError(f"Gemini analysis failed: {e}") from e

    try:
        return json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as e:
        raise AIError(f"Gemini returned an unparseable response: {e}") from e


def ask_profile(username: str, rows: list[dict], question: str) -> str:
    if not question or not question.strip():
        raise AIError("Please enter a question.")

    tweets_block = _format_tweets_for_prompt(rows)
    prompt = f"""You are answering questions about the X/Twitter account @{username}
using ONLY the {len(rows)} posts listed below as your source of truth. If the
answer cannot be determined from these posts, say so plainly instead of
guessing or using outside knowledge about this account or person.

POSTS:
{tweets_block}

QUESTION: {question.strip()}

Answer concisely and cite specific posts (by their [number]) where relevant."""

    try:
        response = _client().models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2),
        )
    except Exception as e:
        raise AIError(f"Gemini could not answer: {e}") from e

    return (response.text or "").strip()
